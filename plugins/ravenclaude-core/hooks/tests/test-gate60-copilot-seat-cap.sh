#!/usr/bin/env bash
# test-gate60-copilot-seat-cap.sh — Gate 60 fixture for PR B (Phase 2, v0.112.0).
#
# Asserts that thing-decision.py's resolve_panel_config() raises the per-seat
# soft cap from 45s to 90s (and the panel deadline from 75s to 105s) when the
# THING_HOST=copilot env signal is set, removing the abstain-on-cold-start
# lockout documented in v0.60.0 from running under Copilot CLI.
#
# Five subtests:
#   G60.A  Default — THING_HOST unset → seat=45, panel=75 (unchanged)
#   G60.B  Copilot — THING_HOST=copilot → seat=90, panel=105 (raised)
#   G60.C  Other host — THING_HOST=claude-code → seat=45 (not bumped)
#   G60.D  User override preserved — thing.yaml sets seat_timeout_seconds=60,
#          THING_HOST=copilot → stays at 60 (explicit override wins)
#   G60.E  Must-fail half — patch resolve_panel_config to skip the bump,
#          assert G60.B now FAILS, proving the gate has teeth
#
# Run directly:   bash plugins/ravenclaude-core/hooks/tests/test-gate60-copilot-seat-cap.sh
# Run via gate:   bash scripts/audit-gates.sh --check 60

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

DECISION_PY="$REPO_ROOT/plugins/ravenclaude-core/scripts/thing-decision.py"
PASS=0
FAIL=0

pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

run_assert() {
  local name="$1"; shift
  local expected_seat="$1"; shift
  local expected_panel="$1"; shift
  local thing_host="${1:-}"
  local thing_yaml_content="${2:-}"

  TMPROOT="$(mktemp -d)"
  if [[ -n "$thing_yaml_content" ]]; then
    mkdir -p "$TMPROOT/.ravenclaude"
    printf '%s' "$thing_yaml_content" > "$TMPROOT/.ravenclaude/thing.yaml"
  fi

  # Run the loader with the controlled environment + tmp root.
  local result
  result="$(THING_HOST="$thing_host" python3 - "$DECISION_PY" "$TMPROOT" <<'PY' 2>/dev/null
import sys, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("td", sys.argv[1])
td = importlib.util.module_from_spec(spec)
spec.loader.exec_module(td)
cfg, _ = td.resolve_panel_config(Path(sys.argv[2]), posture=None)
print(f"{cfg['seat_timeout_seconds']} {cfg['panel_deadline_seconds']}")
PY
)"

  rm -rf "$TMPROOT"

  local actual_seat actual_panel
  actual_seat="$(echo "$result" | awk '{print $1}')"
  actual_panel="$(echo "$result" | awk '{print $2}')"

  if [[ "$actual_seat" == "$expected_seat" && "$actual_panel" == "$expected_panel" ]]; then
    pass "$name: seat=${actual_seat}s panel=${actual_panel}s (expected)"
    return 0
  else
    fail "$name: got seat=${actual_seat:-?}s panel=${actual_panel:-?}s, expected seat=${expected_seat}s panel=${expected_panel}s"
    return 1
  fi
}

echo
echo "── G60.A: default — THING_HOST unset → seat=45, panel=75 ─────────────────"
run_assert "G60.A" 45 75 "" ""

echo
echo "── G60.B: Copilot — THING_HOST=copilot → seat=90, panel=105 ──────────────"
run_assert "G60.B" 90 105 "copilot" ""

echo
echo "── G60.C: other host — THING_HOST=claude-code → seat=45 (unchanged) ──────"
run_assert "G60.C" 45 75 "claude-code" ""

echo
echo "── G60.D: user override preserved — thing.yaml seat=60, THING_HOST=copilot"
# YAML override sets seat_timeout_seconds=60; even with THING_HOST=copilot the
# explicit override must win (the bump only fires when value == _DEFAULT_SEAT_TIMEOUT).
USER_YAML="seat_timeout_seconds: 60
panel_deadline_seconds: 80
"
run_assert "G60.D" 60 80 "copilot" "$USER_YAML"

echo
echo "── G60.E: must-fail half — patched (no-bump) loader keeps default ────────"
# Make a tmp copy of thing-decision.py with the bump block stripped, source it,
# verify G60.B-shape input now returns seat=45 (proving the gate has teeth).
PATCH_TMP="$(mktemp -d)"
PATCH_PY="$PATCH_TMP/thing-decision-nobump.py"
# Strip the Copilot-aware bump (lines containing the os.environ.get THING_HOST block).
python3 - <<PY
import re
src = open("$DECISION_PY").read()
# Remove the Phase 2 bump block (matches the comment + the if block through panel_deadline_seconds line).
patched = re.sub(
    r"    # Phase 2.*?cfg\[\"panel_deadline_seconds\"\] = 105\n",
    "",
    src,
    count=1,
    flags=re.DOTALL,
)
open("$PATCH_PY", "w").write(patched)
PY

# Re-run with THING_HOST=copilot against the patched loader; expect seat=45.
result="$(THING_HOST=copilot python3 - "$PATCH_PY" "$PATCH_TMP" <<'PY' 2>/dev/null
import sys, importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("td", sys.argv[1])
td = importlib.util.module_from_spec(spec)
spec.loader.exec_module(td)
cfg, _ = td.resolve_panel_config(Path(sys.argv[2]), posture=None)
print(f"{cfg['seat_timeout_seconds']} {cfg['panel_deadline_seconds']}")
PY
)"
rm -rf "$PATCH_TMP"

actual_seat="$(echo "$result" | awk '{print $1}')"
if [[ "$actual_seat" == "45" ]]; then
  pass "G60.E must-fail half: patched (no-bump) loader returns seat=45 — confirms G60.B has teeth"
else
  fail "G60.E must-fail half: patched loader returned seat=${actual_seat:-?}, expected 45 (the patch may not have stripped the bump)"
fi

echo
if [[ "$FAIL" -eq 0 ]]; then
  echo "Gate 60 (Copilot-aware seat cap): ALL ASSERTIONS PASS"
  exit 0
else
  echo "Gate 60 (Copilot-aware seat cap): $FAIL assertion(s) FAILED"
  echo ""
  echo "Expected failures if PR B is not yet integrated:"
  echo "  G60.B — seat=45 (not bumped to 90 under THING_HOST=copilot)"
  echo "  G60.E — seat=90 (the unpatched loader bumps; the patch couldn't strip what wasn't there)"
  echo ""
  echo "These failures are CORRECT fixture behavior — they prove the fixtures have teeth."
  exit 1
fi
