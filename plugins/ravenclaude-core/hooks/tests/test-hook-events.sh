#!/usr/bin/env bash
# test-hook-events.sh — fixture-based test for the structured hook-event
# substrate (P0.2). Exercises _emit-event.sh directly AND through the three
# wired hooks (enforce-layout / guard-destructive / guard-recursive-spawn),
# asserting that each deny/warn produces exactly one valid JSON line in
# .ravenclaude/runs/<session>/hook-events.jsonl, and that clean inputs emit
# nothing. Exits 0 only if every assertion holds.
#
# Run directly:   bash plugins/ravenclaude-core/hooks/tests/test-hook-events.sh
# Run via gate:   invoked by scripts/audit-gates.sh Gate 36.

set -uo pipefail

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0
pass() { printf '  ✓ %s\n' "$1"; }
fail() { printf '  ✗ %s\n' "$1"; FAILED=$((FAILED + 1)); }

# A destructive command composed from pieces so this file never contains the
# literal pattern verbatim (keeps greppers/guards from flagging the test file).
FORCED_PUSH="git push --""force origin main"

# ── 1. Direct helper: valid JSON + fail-safe with no project dir ─────────────
T1="$(mktemp -d)"
(
  export CLAUDE_PROJECT_DIR="$T1" CLAUDE_SESSION_ID="t1"
  # shellcheck source=/dev/null
  source "$HOOKS_DIR/_emit-event.sh"
  _emit_hook_event "demo.sh" "deny" "Edit" 'a/b"c\d.md' "demo-rule" 2
)
LOG1="$T1/.ravenclaude/runs/t1/hook-events.jsonl"
if [[ -f "$LOG1" ]] && [[ "$(wc -l < "$LOG1")" -eq 1 ]] && jq -e . < "$LOG1" >/dev/null 2>&1; then
  pass "helper emits exactly one valid JSON line (with quote/backslash in path)"
else
  fail "helper did not emit one valid JSON line"
fi
# fail-safe: unset project dir → no throw, no file
(
  unset CLAUDE_PROJECT_DIR
  # shellcheck source=/dev/null
  source "$HOOKS_DIR/_emit-event.sh"
  _emit_hook_event "demo.sh" "deny" "Edit" "p" "r" 2
)
rc=$?
[[ "$rc" -eq 0 ]] && pass "helper is fail-safe (returns 0 with no project dir)" || fail "helper threw with no project dir (rc=$rc)"
rm -rf "$T1"

# ── 2. enforce-layout deny → one event ───────────────────────────────────────
T2="$(mktemp -d)"
mkdir -p "$T2"
printf '{ "allowed_globs": ["src/**"], "forbidden_globs": [], "suggestions": {} }\n' > "$T2/.repo-layout.json"
CLAUDE_PROJECT_DIR="$T2" CLAUDE_SESSION_ID="t2" "$HOOKS_DIR/enforce-layout.sh" "$T2/off/pattern.md" >/dev/null 2>&1
rc=$?
LOG2="$T2/.ravenclaude/runs/t2/hook-events.jsonl"
if [[ "$rc" -eq 2 ]] && [[ -f "$LOG2" ]] && [[ "$(wc -l < "$LOG2")" -eq 1 ]] \
   && [[ "$(jq -r .verdict "$LOG2")" == "deny" ]] && [[ "$(jq -r .hook "$LOG2")" == "enforce-layout.sh" ]]; then
  pass "enforce-layout deny emits one deny event (exit 2)"
else
  fail "enforce-layout deny event wrong (rc=$rc)"
fi
# clean in-pattern write → no event
CLAUDE_PROJECT_DIR="$T2" CLAUDE_SESSION_ID="t2clean" "$HOOKS_DIR/enforce-layout.sh" "$T2/src/ok.ts" >/dev/null 2>&1
[[ ! -f "$T2/.ravenclaude/runs/t2clean/hook-events.jsonl" ]] && pass "enforce-layout allow emits no event" || fail "enforce-layout emitted on a clean write"
rm -rf "$T2"

# ── 3. guard-destructive deny → one event ────────────────────────────────────
T3="$(mktemp -d)"
printf '{"tool_input":{"command":"%s"}}' "$FORCED_PUSH" \
  | CLAUDE_PROJECT_DIR="$T3" CLAUDE_SESSION_ID="t3" "$HOOKS_DIR/guard-destructive.sh" >/dev/null 2>&1
rc=$?
LOG3="$T3/.ravenclaude/runs/t3/hook-events.jsonl"
if [[ "$rc" -eq 2 ]] && [[ -f "$LOG3" ]] && [[ "$(wc -l < "$LOG3")" -eq 1 ]] \
   && [[ "$(jq -r .verdict "$LOG3")" == "deny" ]] && [[ "$(jq -r .tool "$LOG3")" == "Bash" ]]; then
  pass "guard-destructive deny emits one deny event (exit 2)"
else
  fail "guard-destructive deny event wrong (rc=$rc)"
fi
# benign command → no event
printf '{"tool_input":{"command":"echo hello"}}' \
  | CLAUDE_PROJECT_DIR="$T3" CLAUDE_SESSION_ID="t3clean" "$HOOKS_DIR/guard-destructive.sh" >/dev/null 2>&1
[[ ! -f "$T3/.ravenclaude/runs/t3clean/hook-events.jsonl" ]] && pass "guard-destructive allow emits no event" || fail "guard-destructive emitted on a benign command"
rm -rf "$T3"

# ── 4. guard-recursive-spawn warn → one event ────────────────────────────────
T4="$(mktemp -d)"
AF="$T4/plugins/x/agents/bad.md"; mkdir -p "$(dirname "$AF")"
printf 'You should spawn an agent to handle the subtask.\n' > "$AF"
CLAUDE_PROJECT_DIR="$T4" CLAUDE_SESSION_ID="t4" "$HOOKS_DIR/guard-recursive-spawn.sh" "$AF" >/dev/null 2>&1
LOG4="$T4/.ravenclaude/runs/t4/hook-events.jsonl"
if [[ -f "$LOG4" ]] && [[ "$(wc -l < "$LOG4")" -eq 1 ]] && [[ "$(jq -r .verdict "$LOG4")" == "warn" ]]; then
  pass "guard-recursive-spawn emits one warn event"
else
  fail "guard-recursive-spawn warn event wrong"
fi
# clean agent file → no event
CF="$T4/plugins/x/agents/good.md"
printf 'This agent escalates a handoff recommendation to the Team Lead.\n' > "$CF"
CLAUDE_PROJECT_DIR="$T4" CLAUDE_SESSION_ID="t4clean" "$HOOKS_DIR/guard-recursive-spawn.sh" "$CF" >/dev/null 2>&1
[[ ! -f "$T4/.ravenclaude/runs/t4clean/hook-events.jsonl" ]] && pass "guard-recursive-spawn emits no event on a clean agent file" || fail "guard-recursive-spawn emitted on a clean file"
rm -rf "$T4"

# ── 5. SESSION ISOLATION (red-team FM1) ──────────────────────────────────────
# Native Claude Code does NOT export CLAUDE_SESSION_ID to hooks; the id is on the
# stdin payload's .session_id. The helper must derive it from the caller's
# $payload when CLAUDE_SESSION_ID is unset, so each session lands in its OWN
# runs/<id>/ dir instead of all colliding into runs/unknown/. Bidirectional:
#  (a) payload session_id, env UNSET  → runs/<that-id>/, NOT runs/unknown/
#  (b) env CLAUDE_SESSION_ID set       → env wins over the payload value
#  (c) no payload, no env              → runs/unknown/ (arg-only-hook fallback)
#  (d) traversal-shaped session_id     → sanitized, cannot escape runs/
T5="$(mktemp -d)"

# (a) Drive guard-destructive via stdin with a session_id and NO env var.
(
  export CLAUDE_PROJECT_DIR="$T5/a"; mkdir -p "$CLAUDE_PROJECT_DIR"
  unset CLAUDE_SESSION_ID
  printf '{"session_id":"sess-iso-A","tool_input":{"command":"%s"}}' "$FORCED_PUSH" \
    | "$HOOKS_DIR/guard-destructive.sh" >/dev/null 2>&1
)
LOG5A="$T5/a/.ravenclaude/runs/sess-iso-A/hook-events.jsonl"
if [[ -f "$LOG5A" ]] && [[ ! -d "$T5/a/.ravenclaude/runs/unknown" ]] \
   && [[ "$(jq -r .session_id "$LOG5A")" == "sess-iso-A" ]]; then
  pass "native session id (from stdin payload) lands in runs/sess-iso-A/, not runs/unknown/"
else
  fail "session isolation: payload session_id did NOT route to runs/sess-iso-A/"
fi

# (b) An explicit CLAUDE_SESSION_ID export wins over the payload value.
(
  export CLAUDE_PROJECT_DIR="$T5/b"; mkdir -p "$CLAUDE_PROJECT_DIR"
  export CLAUDE_SESSION_ID="env-sid-B"
  printf '{"session_id":"payload-sid-B","tool_input":{"command":"%s"}}' "$FORCED_PUSH" \
    | "$HOOKS_DIR/guard-destructive.sh" >/dev/null 2>&1
)
if [[ -f "$T5/b/.ravenclaude/runs/env-sid-B/hook-events.jsonl" ]] \
   && [[ ! -d "$T5/b/.ravenclaude/runs/payload-sid-B" ]]; then
  pass "explicit CLAUDE_SESSION_ID wins over payload .session_id"
else
  fail "session isolation: env CLAUDE_SESSION_ID did not win over payload"
fi

# (c) No payload and no env → the documented "unknown" fallback (no regression).
(
  export CLAUDE_PROJECT_DIR="$T5/c"; mkdir -p "$CLAUDE_PROJECT_DIR"
  unset CLAUDE_SESSION_ID
  # shellcheck source=/dev/null
  source "$HOOKS_DIR/_emit-event.sh"
  _emit_hook_event "demo.sh" "deny" "Bash" "p" "r" 2
)
if [[ -f "$T5/c/.ravenclaude/runs/unknown/hook-events.jsonl" ]]; then
  pass "no payload + no env → runs/unknown/ (documented fallback, no regression)"
else
  fail "session isolation: missing-everything case did not fall back to unknown"
fi

# (d) A traversal-shaped payload session_id is sanitized — cannot escape runs/.
(
  export CLAUDE_PROJECT_DIR="$T5/d"; mkdir -p "$CLAUDE_PROJECT_DIR"
  unset CLAUDE_SESSION_ID
  payload='{"session_id":"../../escape"}'
  # shellcheck source=/dev/null
  source "$HOOKS_DIR/_emit-event.sh"
  _emit_hook_event "demo.sh" "deny" "Bash" "p" "r" 2
)
if [[ ! -e "$T5/d/escape" ]] && [[ ! -e "$T5/escape" ]]; then
  pass "traversal-shaped payload session_id is sanitized (no escape from runs/)"
else
  fail "session isolation: traversal session_id escaped the runs/ dir"
fi
rm -rf "$T5"

echo
if [[ "$FAILED" -eq 0 ]]; then
  echo "hook-event substrate: ALL ASSERTIONS PASS"
  exit 0
fi
echo "hook-event substrate: $FAILED assertion(s) FAILED"
exit 1
