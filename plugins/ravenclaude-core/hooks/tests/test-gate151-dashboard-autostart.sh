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
#   O1-O4, MF2  ownership (repo-review dashboard-9): a live server is adopted only
#       when /__csrf reports THIS project's id; another project's (or an older,
#       id-less) server is skipped and ours starts on the next port. Driven by a
#       tiny local stand-in that answers /__csrf on a free port window.
#   H1, H2, MF3  launcher resolution (repo-review hooks-20): with CLAUDE_PLUGIN_ROOT
#       unset (the dev mirror) the hook finds its own ../bin/rc, and a missing
#       launcher prints one stderr line instead of exiting silently.
#
# Self-contained: every fixture is a throwaway mktemp project and the launcher is
# a recording stub, so no real dashboard server is started. The ownership rows
# bind a small stand-in listener on free high ports only.
#
# Run directly:  bash plugins/ravenclaude-core/hooks/tests/test-gate151-dashboard-autostart.sh

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# RC_GATE151_HOOK_UNDER_TEST points the suite at another copy of the hook (the teeth
# run: an older hook must turn the O*/H* rows red). Unset in normal runs.
HOOK="${RC_GATE151_HOOK_UNDER_TEST:-$(cd "$SCRIPT_DIR/.." && pwd)/dashboard-autostart.sh}"

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
FAKE_PIDS=""
trap 'for _p in $FAKE_PIDS; do kill "$_p" 2>/dev/null || true; done; rm -rf "$TMP"' EXIT

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

# ── Ownership (repo-review dashboard-9): a live server is adopted only when it
#    reports THIS project's id in /__csrf; anything else -> start on the next port.
#    These rows drive the real curl probe against a real local listener, so no
#    FORCE_* seam is set here.
#   O1  a live server for ANOTHER project on the port      -> launch on port+1
#   O2  a live server for THIS project on the port         -> stand down
#   O3  a live server with no project_id (an older server) -> launch on port+1
#   O4  this project's server already on port+1, other on port -> stand down
#   MF2 teeth: neuter the id comparison -> O1 adopts the foreign server
if command -v curl >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
  FAKE_PY="$TMP/fake_dash.py"
  cat >"$FAKE_PY" <<'PYEOF'
import http.server, json, sys
port, pid = int(sys.argv[1]), sys.argv[2]
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def do_GET(self):
        if self.path != "/__csrf":
            self.send_response(404); self.end_headers(); return
        doc = {"token": "t"}
        if pid != "-":
            doc["project_id"] = pid
        body = json.dumps(doc).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
http.server.HTTPServer(("127.0.0.1", port), H).serve_forever()
PYEOF
  # A 12-port window that is free right now (the hook scans port..port+10).
  WIN="$(python3 -c 'import os, socket
def free(p):
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", p))
        return True
    except OSError:
        return False
    finally:
        s.close()
p = 30000 + (os.getpid() % 500) * 23
while p < 60000:
    if all(free(p + i) for i in range(12)):
        print(p)
        break
    p += 13')"
  project_id_of() {
    python3 -c 'import hashlib, sys
from pathlib import Path
print(hashlib.sha256(str(Path(sys.argv[1]).resolve()).encode("utf-8")).hexdigest()[:12])' "$1"
  }
  FAKE_PIDS=""
  start_fake() { # <port> <project_id or ->
    python3 "$FAKE_PY" "$1" "$2" >/dev/null 2>&1 &
    FAKE_PIDS="$FAKE_PIDS $!"
    local i=0
    while [ $i -lt 50 ]; do
      curl -sf -m 1 -o /dev/null "http://127.0.0.1:$1/__csrf" 2>/dev/null && return 0
      sleep 0.1
      i=$((i + 1))
    done
    return 1
  }
  stop_fakes() {
    for p in $FAKE_PIDS; do kill "$p" 2>/dev/null || true; done
    for p in $FAKE_PIDS; do wait "$p" 2>/dev/null || true; done
    FAKE_PIDS=""
  }
  # run_hook_live <hook> <project> <port> — no FORCE seam; the probe is real.
  run_hook_live() {
    local hook="$1" proj="$2" port="$3" rc=0
    RECORD="$TMP/record.$$.$RANDOM"
    : >"$RECORD"
    env CLAUDE_PROJECT_DIR="$proj" \
      RC_DASH_AUTOSTART_LAUNCHER="$STUB" \
      RC_STUB_RECORD="$RECORD" \
      RC_DASH_AUTOSTART_PORT="$port" \
      bash "$hook" >/dev/null 2>&1 || rc=$?
    local i=0
    while [ $i -lt 30 ]; do
      [ -s "$RECORD" ] && break
      sleep 0.1
      i=$((i + 1))
    done
    return $rc
  }

  if [ -z "$WIN" ]; then
    fail "O*: no free 12-port window to run the ownership rows"
  else
    P1=$((WIN + 1))
    p="$(mk_project o1 "dashboard_autostart: serve")"
    if start_fake "$WIN" "f0f0f0f0f0f0"; then
      run_hook_live "$HOOK" "$p" "$WIN"
      if launched && recorded | grep -q -- "--port $P1"; then
        pass "O1 another project's live server -> not adopted, ours starts on port+1"
      else
        fail "O1 another project's live server was adopted (or launch went elsewhere): $(recorded)"
      fi
    else
      fail "O1 fake server did not come up on $WIN"
    fi
    stop_fakes

    p="$(mk_project o2 "dashboard_autostart: serve")"
    if start_fake "$WIN" "$(project_id_of "$p")"; then
      run_hook_live "$HOOK" "$p" "$WIN"
      if launched; then
        fail "O2 this project's live server: launched a duplicate ($(recorded))"
      else
        pass "O2 this project's live server -> stands down (positive control)"
      fi
    else
      fail "O2 fake server did not come up on $WIN"
    fi
    stop_fakes

    p="$(mk_project o3 "dashboard_autostart: serve")"
    if start_fake "$WIN" "-"; then
      run_hook_live "$HOOK" "$p" "$WIN"
      if launched && recorded | grep -q -- "--port $P1"; then
        pass "O3 a server reporting no project_id -> not adopted, ours starts on port+1"
      else
        fail "O3 a server with no project_id was adopted: $(recorded)"
      fi
    else
      fail "O3 fake server did not come up on $WIN"
    fi
    stop_fakes

    p="$(mk_project o4 "dashboard_autostart: serve")"
    if start_fake "$WIN" "f0f0f0f0f0f0" && start_fake "$P1" "$(project_id_of "$p")"; then
      run_hook_live "$HOOK" "$p" "$WIN"
      if launched; then
        fail "O4 ours already on port+1: launched a duplicate ($(recorded))"
      else
        pass "O4 ours already live on port+1 behind a foreign port -> stands down"
      fi
    else
      fail "O4 fake servers did not come up on $WIN/$P1"
    fi
    stop_fakes

    MUTANT2="$TMP/mutant-owner.sh"
    sed 's/then echo ours; else echo other; fi/then echo ours; else echo ours; fi/' "$HOOK" >"$MUTANT2"
    if cmp -s "$HOOK" "$MUTANT2"; then
      fail "MF2 teeth: the id-comparison mutation did not apply (re-target the sed)"
    else
      p="$(mk_project mf2 "dashboard_autostart: serve")"
      if start_fake "$WIN" "f0f0f0f0f0f0"; then
        run_hook_live "$MUTANT2" "$p" "$WIN"
        if launched; then
          fail "MF2 teeth: with the id comparison neutered the foreign server was STILL skipped — O1 is vacuous"
        else
          pass "MF2 teeth: neutering the id comparison makes the hook adopt the foreign server"
        fi
      else
        fail "MF2 fake server did not come up on $WIN"
      fi
      stop_fakes
    fi
  fi
else
  fail "O*: curl and python3 are required for the ownership rows"
fi

# ── Launcher resolution (repo-review hooks-20) ───────────────────────────────
#   H1  dev-mirror: CLAUDE_PLUGIN_ROOT unset, no override -> the hook's own ../bin/rc
#   H2  no launcher at all -> one stderr line, exit 0, nothing launched
#   MF3 teeth: restore the old ${CLAUDE_PLUGIN_ROOT}/bin/rc default -> H1 goes silent
mk_plugin_copy() { # <dir> <hook-source> [with-launcher]
  mkdir -p "$1/hooks" "$1/bin"
  cp "$2" "$1/hooks/dashboard-autostart.sh"
  chmod +x "$1/hooks/dashboard-autostart.sh"
  if [ "${3:-}" = "with-launcher" ]; then
    cp "$STUB" "$1/bin/rc"
    chmod +x "$1/bin/rc"
  fi
}
run_hook_mirror() { # <hook> <project>  -> exit code; stderr in $ERRF
  local rc=0
  RECORD="$TMP/record.$$.$RANDOM"
  : >"$RECORD"
  ERRF="$TMP/err.$$.$RANDOM"
  env -u CLAUDE_PLUGIN_ROOT -u RC_DASH_AUTOSTART_LAUNCHER \
    CLAUDE_PROJECT_DIR="$2" RC_STUB_RECORD="$RECORD" RC_DASH_AUTOSTART_PORT=8999 \
    RC_DASH_AUTOSTART_FORCE_DEAD=1 \
    bash "$1" >/dev/null 2>"$ERRF" || rc=$?
  local i=0
  while [ $i -lt 30 ]; do
    [ -s "$RECORD" ] && break
    sleep 0.1
    i=$((i + 1))
  done
  return $rc
}

mk_plugin_copy "$TMP/plugA" "$HOOK" with-launcher
p="$(mk_project h1 "dashboard_autostart: serve")"
run_hook_mirror "$TMP/plugA/hooks/dashboard-autostart.sh" "$p"
rc=$?
if launched; then
  pass "H1 dev-mirror (CLAUDE_PLUGIN_ROOT unset) resolves the hook's own ../bin/rc"
else
  fail "H1 dev-mirror: launcher not resolved, nothing started ($(cat "$ERRF" 2>/dev/null))"
fi
[ "$rc" -eq 0 ] && pass "H1 exits 0" || fail "H1 exited $rc"

mk_plugin_copy "$TMP/plugB" "$HOOK"
p="$(mk_project h2 "dashboard_autostart: serve")"
run_hook_mirror "$TMP/plugB/hooks/dashboard-autostart.sh" "$p"
rc=$?
if launched; then
  fail "H2 missing launcher: something was launched"
elif grep -q "launcher not found" "$ERRF" 2>/dev/null; then
  pass "H2 missing launcher -> one stderr line instead of a silent exit"
else
  fail "H2 missing launcher exited silently (stderr: $(cat "$ERRF" 2>/dev/null))"
fi
[ "$rc" -eq 0 ] && pass "H2 exits 0" || fail "H2 exited $rc"

MUTANT3="$TMP/mutant-launcher.sh"
# shellcheck disable=SC2016 # the $ text is the literal line being restored
sed 's|^LAUNCHER=.*|LAUNCHER="${RC_DASH_AUTOSTART_LAUNCHER:-${CLAUDE_PLUGIN_ROOT:-}/bin/rc}"|' "$HOOK" >"$MUTANT3"
if cmp -s "$HOOK" "$MUTANT3"; then
  fail "MF3 teeth: the launcher mutation did not apply (re-target the sed)"
else
  mk_plugin_copy "$TMP/plugC" "$MUTANT3" with-launcher
  p="$(mk_project mf3 "dashboard_autostart: serve")"
  run_hook_mirror "$TMP/plugC/hooks/dashboard-autostart.sh" "$p"
  if launched; then
    fail "MF3 teeth: the old default still launched in the dev mirror — H1 is vacuous"
  else
    pass "MF3 teeth: the old \${CLAUDE_PLUGIN_ROOT}/bin/rc default launches nothing in the dev mirror"
  fi
fi

echo
if [ "$FAIL" -gt 0 ]; then
  printf '  \033[31m%d pass, %d fail\033[0m\n' "$PASS" "$FAIL"
  exit 1
fi
printf '  \033[32m%d pass, 0 fail\033[0m\n' "$PASS"
exit 0
