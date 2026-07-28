#!/usr/bin/env bash
# test-gate151-dashboard-autostart.sh — Gate 151 audit fixture for the opt-in
# dashboard autostart hook (hooks/dashboard-autostart.sh).
#
# Drives the REAL hook against a stub launcher that records its argv, proving the
# contract is bidirectional:
#
#   MUST-NOT-LAUNCH (the absent => OFF default, and the anti-duplicate probe):
#     N1  no comfort-posture.yaml at all
#     N2  dashboard_autostart: off
#     N3  a posture that exists but never mentions the key
#     N4  dashboard_autostart: open  BUT a dashboard already answers on the port
#     N5  dashboard_autostart: yes   (an unrecognised value must never launch —
#         a typo silently starting a server is the failure mode this rules out)
#   MUST-LAUNCH:
#     L1  dashboard_autostart: open   -> launcher invoked WITHOUT --no-open
#     L2  dashboard_autostart: serve  -> launcher invoked WITH    --no-open
#   E   every case above exits 0 (SessionStart hooks cannot block, and a
#       dashboard that fails to come up must never stop a session starting)
#   MF  teeth half — neuter the mode gate and assert N2 (`off`) NOW launches,
#       proving the off/absent no-op is real code and not a vacuous pass.
#
# Self-contained: every fixture is a throwaway mktemp project and the launcher is
# a recording stub, so no server is ever started and no real port is touched.
#
# Run directly:  bash plugins/ravenclaude-core/hooks/tests/test-gate151-dashboard-autostart.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$(cd "$SCRIPT_DIR/.." && pwd)/dashboard-autostart.sh"

PASS=0
FAIL=0
pass() {
  printf '  \033[32m✓\033[0m %s\n' "$1"
  PASS=$((PASS + 1))
}
fail() {
  printf '  \033[31m✗\033[0m %s\n' "$1"
  FAIL=$((FAIL + 1))
}

[ -x "$HOOK" ] || {
  echo "FAIL: hook not executable at $HOOK"
  exit 1
}

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# ── fixture helpers ──────────────────────────────────────────────────────────

# mk_project <name> [posture-body] — a scratch project dir; posture written only
# when a body is supplied (so the "no posture at all" case is expressible).
mk_project() {
  local d="$TMP/$1"
  mkdir -p "$d/.ravenclaude"
  if [ $# -ge 2 ]; then
    printf '%s\n' "schema_version: 5" "$2" >"$d/.ravenclaude/comfort-posture.yaml"
  fi
  printf '%s' "$d"
}

# The recording stub stands in for bin/rc: it appends its argv and exits.
STUB="$TMP/rc-stub"
cat >"$STUB" <<'STUBEOF'
#!/usr/bin/env bash
printf '%s\n' "$*" >>"$RC_STUB_RECORD"
STUBEOF
chmod +x "$STUB"

# run_hook <hook-path> <project-dir> <live|dead> — returns the hook's exit code;
# the stub's argv (if any) lands in $RECORD.
RECORD=""
run_hook() {
  local hook="$1" proj="$2" liveness="$3" rc=0
  RECORD="$TMP/record.$$.$RANDOM"
  : >"$RECORD"
  local live_env="RC_DASH_AUTOSTART_FORCE_DEAD=1"
  [ "$liveness" = "live" ] && live_env="RC_DASH_AUTOSTART_FORCE_LIVE=1"
  env CLAUDE_PROJECT_DIR="$proj" \
    RC_DASH_AUTOSTART_LAUNCHER="$STUB" \
    RC_STUB_RECORD="$RECORD" \
    RC_DASH_AUTOSTART_PORT=8999 \
    "$live_env" \
    bash "$hook" >/dev/null 2>&1 || rc=$?
  # The launch is detached (nohup ... &), so poll briefly for the stub's write.
  local i=0
  while [ $i -lt 30 ]; do
    [ -s "$RECORD" ] && break
    sleep 0.1
    i=$((i + 1))
  done
  return $rc
}

launched() { [ -s "$RECORD" ]; }
recorded() { cat "$RECORD" 2>/dev/null; }

echo "── Gate 151: dashboard autostart (opt-in, absent => OFF) ─────────────────"

# ── MUST-NOT-LAUNCH ──────────────────────────────────────────────────────────
p="$(mk_project n1)"
run_hook "$HOOK" "$p" dead
rc=$?
if launched; then fail "N1 no posture file: launched (must be a no-op)"; else pass "N1 no posture file -> no launch"; fi
[ "$rc" -eq 0 ] && pass "N1 exits 0" || fail "N1 exited $rc (must always exit 0)"

p="$(mk_project n2 "dashboard_autostart: off")"
run_hook "$HOOK" "$p" dead
rc=$?
if launched; then fail "N2 'off': launched (the explicit off must no-op)"; else pass "N2 'off' -> no launch"; fi
[ "$rc" -eq 0 ] && pass "N2 exits 0" || fail "N2 exited $rc"

p="$(mk_project n3 "design_checkins: true")"
run_hook "$HOOK" "$p" dead
rc=$?
if launched; then fail "N3 key absent: launched (absent must mean OFF)"; else pass "N3 key absent -> no launch"; fi
[ "$rc" -eq 0 ] && pass "N3 exits 0" || fail "N3 exited $rc"

p="$(mk_project n4 "dashboard_autostart: open")"
run_hook "$HOOK" "$p" live
rc=$?
if launched; then
  fail "N4 already-live: launched a SECOND server (concurrent sessions would duplicate)"
else
  pass "N4 already-live -> stands down, no second server/tab"
fi
[ "$rc" -eq 0 ] && pass "N4 exits 0" || fail "N4 exited $rc"

p="$(mk_project n5 "dashboard_autostart: yes")"
run_hook "$HOOK" "$p" dead
rc=$?
if launched; then fail "N5 unrecognised value: launched (a typo must never start a server)"; else pass "N5 unrecognised value -> no launch"; fi
[ "$rc" -eq 0 ] && pass "N5 exits 0" || fail "N5 exited $rc"

# ── MUST-LAUNCH ──────────────────────────────────────────────────────────────
p="$(mk_project l1 "dashboard_autostart: open")"
run_hook "$HOOK" "$p" dead
rc=$?
if launched; then
  pass "L1 'open' -> launches"
  if recorded | grep -q -- "--no-open"; then
    fail "L1 'open' passed --no-open (that is the 'serve' mode; no tab would open)"
  else
    pass "L1 'open' omits --no-open (a browser tab opens)"
  fi
  recorded | grep -q -- "dashboard" && pass "L1 invokes the 'dashboard' verb" || fail "L1 did not invoke 'dashboard'"
else
  fail "L1 'open': did not launch"
fi
[ "$rc" -eq 0 ] && pass "L1 exits 0" || fail "L1 exited $rc"

p="$(mk_project l2 "dashboard_autostart: serve")"
run_hook "$HOOK" "$p" dead
rc=$?
if launched; then
  pass "L2 'serve' -> launches"
  if recorded | grep -q -- "--no-open"; then
    pass "L2 'serve' passes --no-open (server only, no tab)"
  else
    fail "L2 'serve' omitted --no-open (a tab would open in headless mode)"
  fi
else
  fail "L2 'serve': did not launch"
fi
[ "$rc" -eq 0 ] && pass "L2 exits 0" || fail "L2 exited $rc"

# ── MF teeth: neuter the mode gate; 'off' must then launch ───────────────────
MUTANT="$TMP/mutant-autostart.sh"
sed 's/^  \*) exit 0 ;;$/  *) MODE=open ;;/' "$HOOK" >"$MUTANT"
chmod +x "$MUTANT"
if cmp -s "$HOOK" "$MUTANT"; then
  fail "MF teeth: the mutation did not apply (the mode-gate line moved — re-target the sed)"
else
  p="$(mk_project mf "dashboard_autostart: off")"
  run_hook "$MUTANT" "$p" dead
  if launched; then
    pass "MF teeth: neutering the mode gate makes 'off' launch (the no-op is real code)"
  else
    fail "MF teeth: 'off' still did not launch with the gate neutered — the N2 pass is vacuous"
  fi
fi

echo
if [ "$FAIL" -gt 0 ]; then
  printf '  \033[31m%d pass, %d fail\033[0m\n' "$PASS" "$FAIL"
  exit 1
fi
printf '  \033[32m%d pass, 0 fail\033[0m\n' "$PASS"
exit 0
