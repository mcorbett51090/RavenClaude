#!/usr/bin/env bash
# test-advisory-delivery.sh — asserts the ADVISORY TIER reaches the model.
#
# ⛔ WHY THIS TEST EXISTS. Measured 2026-08-19: every advisory hook wrote to stderr
# and exited 0, and that channel is UNDELIVERED to the model on PostToolUse,
# PreToolUse and Stop alike (matched trials, positive control on every run — see
# hooks/_advise.sh). The advisory tier had been talking to the terminal for its
# whole service life. This test is the regression gate for the repair.
#
# ⛔ THE PRE-EXISTING TESTS CANNOT CATCH THIS. test-gate223-probe-validity.sh and
# friends assert on STDERR, which the repair deliberately preserves — so they pass
# both before and after, and would pass again if the repair were reverted. A test
# that cannot distinguish repaired from broken is not a gate. This one keys on the
# NEW channel, and its canary proves it can tell the difference.
set -uo pipefail

HD="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
fails=0
ok()   { printf '  OK   %s\n' "$1"; }
bad()  { printf '  FAIL %s\n' "$1"; fails=$((fails+1)); }

# ── 1. the helper proves itself first (Rule 6: instrument before verdict) ────
if bash "$HD/_advise.sh" --self-test >/dev/null 2>&1; then
  ok "_advise.sh self-test passes"
else
  bad "_advise.sh self-test FAILED — nothing below is trustworthy"
fi

# ── 2. a real rewired hook emits the delivered envelope ─────────────────────
proj="$TMP/proj"; mkdir -p "$proj/.ravenclaude"
printf 'probe_validity: on\n' > "$proj/.ravenclaude/comfort-posture.yaml"
payload="$TMP/p.json"
printf '%s' "{\"session_id\":\"t\",\"cwd\":\"$proj\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"grep -qv alpha mixed.txt\"}}" > "$payload"

CLAUDE_PROJECT_DIR="$proj" bash "$HD/guard-probe-validity.sh" < "$payload" > "$TMP/out" 2> "$TMP/err"
rc=$?

[ "$rc" -eq 0 ] && ok "exit 0 preserved (fail-safe contract intact)" \
                || bad "exit was $rc, expected 0 — fail-safe contract BROKEN"

if grep -q 'additionalContext' "$TMP/out"; then
  ok "emits an additionalContext envelope on stdout (the DELIVERED channel)"
else
  bad "no additionalContext on stdout — the advisory is undelivered again"
fi

if grep -q 'RavenClaude guard notice' "$TMP/out"; then
  ok "carries the self-identifying banner"
else
  bad "banner missing — measured: an unlabelled advisory is discounted as injection"
fi

if python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$TMP/out" 2>/dev/null; then
  ok "stdout is well-formed JSON"
else
  bad "stdout is not valid JSON — the host will discard it"
fi

if grep -q 'probe-validity' "$TMP/err"; then
  ok "the original stderr UI notice is PRESERVED (no regression)"
else
  bad "stderr notice lost — the repair must be additive, not a swap"
fi

# ── 3. ⛔ CANARY — prove this test can tell repaired from broken ─────────────
# Strip the rewire from a COPY and assert the additionalContext check fails on it.
# Without this, a test that always passes looks identical to a test that works.
cp "$HD/guard-probe-validity.sh" "$TMP/unpatched.sh"
cp "$HD/_advise.sh" "$TMP/_advise.sh"
python3 - "$TMP/unpatched.sh" <<'PY'
import re, sys
p = sys.argv[1]
s = open(p).read()
s = s.replace('rc_advise_init PreToolUse 0', 'true')   # neuter the repair only
open(p, "w").write(s)
PY
CLAUDE_PROJECT_DIR="$proj" bash "$TMP/unpatched.sh" < "$payload" > "$TMP/out2" 2>/dev/null
if grep -q 'additionalContext' "$TMP/out2"; then
  bad "CANARY DID NOT BITE — the neutered hook still emitted additionalContext, so this test proves nothing"
else
  ok "canary bites: the neutered hook emits NO additionalContext"
fi

echo
if [ "$fails" -eq 0 ]; then
  echo "test-advisory-delivery: PASS"
else
  echo "test-advisory-delivery: FAIL ($fails)"
fi
exit "$fails"
