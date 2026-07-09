#!/usr/bin/env bash
# test-gate80-status-launcher-check.sh — Gate 80 fixture for v0.113.2 / v0.114.0.
#
# Asserts that `ravenclaude status` detects a missing dashboard launcher
# (Contoso's pre-v0.44.0 install case) AND that `ravenclaude status --fix`
# installs it via wire_dashboard_launchers().
#
# Closes the PM panel's "dashboard_launcher_present check on ravenclaude
# status" recommendation from the 2026-06-03 Copilot adapter triage.
#
# Subtests:
#   G80.A  status (no flags) on a project WITHOUT the launcher reports MISSING
#          and prints the --fix command
#   G80.B  status --fix on the same project installs dashboard.sh + README.md
#          + .vscode/tasks.json
#   G80.C  status (no flags) AFTER --fix reports "present"
#   G80.D  Must-fail half — patched cmd_status with the launcher check stripped
#          fails to detect MISSING on a launcher-absent project
#
# Run directly:   bash plugins/ravenclaude-core/hooks/tests/test-gate80-status-launcher-check.sh
# Run via gate:   bash scripts/audit-gates.sh --check 80

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

RAVENCLAUDE="$REPO_ROOT/scripts/ravenclaude"
PASS=0
FAIL=0

pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

# Make a tmp project that looks like Contoso's pre-v0.44.0 state: skills + hooks
# wired, but no dashboard.sh / README.md / .vscode/tasks.json.
make_tmp_project() {
  local p; p="$(mktemp -d)"
  mkdir -p "$p/.claude/skills/sample"
  mkdir -p "$p/.github/hooks"
  printf '{}' > "$p/.github/hooks/ravenclaude.json"
  printf '%s' "$p"
}

echo
echo "── G80.A: status (no flags) reports MISSING + prints --fix command ───────"
T1="$(make_tmp_project)"
OUT_A="$(bash "$RAVENCLAUDE" status --project "$T1" 2>&1)"
if printf '%s' "$OUT_A" | grep -q 'launcher: MISSING'; then
  pass "G80.A: status correctly reports launcher: MISSING"
else
  fail "G80.A: status did NOT report 'launcher: MISSING' on a launcher-absent project"
fi
if printf '%s' "$OUT_A" | grep -q "ravenclaude status --fix"; then
  pass "G80.A: status prints the --fix remediation hint"
else
  fail "G80.A: status did NOT print the --fix remediation hint"
fi
rm -rf "$T1"

echo
echo "── G80.B: status --fix installs the launcher files ───────────────────────"
T2="$(make_tmp_project)"
OUT_B="$(bash "$RAVENCLAUDE" status --project "$T2" --fix 2>&1)"
B_OK=1
[ -f "$T2/.ravenclaude/dashboard.sh" ] || { fail "G80.B: dashboard.sh not installed"; B_OK=0; }
[ -f "$T2/.ravenclaude/README.md" ]    || { fail "G80.B: README.md not installed"; B_OK=0; }
[ -f "$T2/.vscode/tasks.json" ]         || { fail "G80.B: .vscode/tasks.json not installed"; B_OK=0; }
[ -x "$T2/.ravenclaude/dashboard.sh" ]  || { fail "G80.B: dashboard.sh not executable"; B_OK=0; }
[ "$B_OK" -eq 1 ] && pass "G80.B: --fix installed dashboard.sh + README.md + .vscode/tasks.json (all executable/present)"

echo
echo "── G80.C: status AFTER --fix reports launcher present ────────────────────"
OUT_C="$(bash "$RAVENCLAUDE" status --project "$T2" 2>&1)"
if printf '%s' "$OUT_C" | grep -q "launcher: .ravenclaude/dashboard.sh + README.md + VS Code task present"; then
  pass "G80.C: status after --fix reports launcher present"
else
  fail "G80.C: status after --fix did NOT report launcher present (output: $(printf '%s' "$OUT_C" | grep launcher || echo NO_LAUNCHER_LINE))"
fi
rm -rf "$T2"

echo
echo "── G80.D: must-fail half — patched cmd_status (no launcher check) ────────"
PATCH_TMP="$(mktemp -d)"
PATCHED_RC="$PATCH_TMP/ravenclaude-patched"
# Strip the launcher-check block from cmd_status (the block beginning with
# `# Dashboard launcher check` and ending with the closing `fi` before
# function close).
python3 - <<PY
import re
src = open("$RAVENCLAUDE").read()
patched = re.sub(
    r"  # Dashboard launcher check.*?\n  fi\n}",
    "}",
    src,
    count=1,
    flags=re.DOTALL,
)
open("$PATCHED_RC", "w").write(patched)
PY
chmod +x "$PATCHED_RC"

T3="$(make_tmp_project)"
# Set CORE so the patched script can still find templates (same as the real one).
export CORE="$REPO_ROOT/plugins/ravenclaude-core"
OUT_D="$(bash "$PATCHED_RC" status --project "$T3" 2>&1)"
if printf '%s' "$OUT_D" | grep -q "launcher: MISSING"; then
  fail "G80.D: patched (no-check) script STILL reported MISSING — patch didn't strip the block"
else
  pass "G80.D must-fail half: patched (no-check) script does NOT report MISSING — confirms G80.A has teeth"
fi
rm -rf "$T3" "$PATCH_TMP"

echo
if [ "$FAIL" -eq 0 ]; then
  echo "Gate 80 (ravenclaude status launcher check): ALL ASSERTIONS PASS"
  exit 0
else
  echo "Gate 80 (ravenclaude status launcher check): $FAIL assertion(s) FAILED"
  exit 1
fi
