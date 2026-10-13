#!/usr/bin/env bash
# test-gate300-dashboard-prompt.sh — Gate 300 fixture (v0.353.0).
#
# Proves scripts/dashboard-prompt.sh does the ONE thing it exists for and nothing
# else: tell a person with no comfort posture how to open the dashboard.
#
#   P1  unconfigured project  -> valid JSON, BOTH channels (systemMessage for the
#                                person, additionalContext for the agent), names
#                                /dashboard and the dashboard_autostart knob
#   P2  posture file present  -> silent (the entire gate is one file test)
#   P3  RC_DASHBOARD_PROMPT=off -> silent
#   P4  writes NOTHING        -> project tree and HOME unchanged after a run
#   P5  edition wording       -> with no ../bin/rc beside it, the hosted-page
#                                wording is used and rc / autostart are NOT named
#   P6  fail-safe             -> nonexistent project dir: exit 0, silent
#   P7  no-egress             -> a sentinel in the stdin payload and in the env
#                                never appears in the output (Gate 19's rule)
#   P8  registered            -> hooks.json (SessionStart startup|resume|clear|fork)
#                                AND the dev-mirror .claude/settings.json
#   T1  teeth: a mutant with the posture gate REMOVED must speak in a configured
#       project — proving P2 depends on that gate and is not passing vacuously
#   T2  teeth: a mutant that echoes stdin must be caught by the P7 check
#
# Run directly:   bash plugins/ravenclaude-core/hooks/tests/test-gate300-dashboard-prompt.sh
# Run via gate:   bash scripts/audit-gates.sh --check 300
#
# Portability: bash 3.2; no sed -i / grep -P / GNU timeout. python3 is used only to
# PARSE the hook's JSON output (the hook itself needs no python3).

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT" || exit 1
SCRIPT="plugins/ravenclaude-core/scripts/dashboard-prompt.sh"
PASS=0
FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

[ -f "$SCRIPT" ] || { fail "P0 $SCRIPT missing"; echo "dashboard-prompt: $PASS passed, $FAIL failed"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "python3 required to parse hook JSON"; exit 1; }

TMP="$(mktemp -d 2>/dev/null || mktemp -d -t dp)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/empty" "$TMP/cfg/.ravenclaude" "$TMP/home" "$TMP/ed/scripts"
: > "$TMP/cfg/.ravenclaude/comfort-posture.yaml"
cp "$SCRIPT" "$TMP/ed/scripts/dashboard-prompt.sh" # no ../bin/rc beside this copy

# run <script> <project_dir> [extra env assignments...] -> stdout; stdin is a payload
run() {
  local script="$1" proj="$2"
  shift 2
  printf '%s' '{"hook_event_name":"SessionStart","source":"startup","secret_probe":"PAYLOAD_SENTINEL_7f3a"}' |
    env -i PATH="$PATH" HOME="$TMP/home" CLAUDE_PROJECT_DIR="$proj" ENV_SENTINEL="ENV_SENTINEL_9c1d" "$@" bash "$script" 2>/dev/null
}
json_field() { # json-on-stdin field-path -> value ('' if absent/invalid)
  python3 -c '
import sys, json
try:
    d = json.loads(sys.stdin.read())
    for k in sys.argv[1].split("."):
        d = d[k]
    print(d)
except Exception:
    pass' "$1"
}

# ── P1 ───────────────────────────────────────────────────────────────────────
out="$(run "$SCRIPT" "$TMP/empty")"; rc=$?
sysmsg="$(printf '%s' "$out" | json_field systemMessage)"
ctx="$(printf '%s' "$out" | json_field hookSpecificOutput.additionalContext)"
ev="$(printf '%s' "$out" | json_field hookSpecificOutput.hookEventName)"
[ "$rc" = 0 ] && pass "P1a exits 0" || fail "P1a exit $rc"
[ -n "$sysmsg" ] && pass "P1b systemMessage present (what the PERSON sees)" || fail "P1b systemMessage missing or output not valid JSON"
[ -n "$ctx" ] && [ "$ev" = "SessionStart" ] && pass "P1c additionalContext present with hookEventName SessionStart (what the AGENT sees)" || fail "P1c additionalContext/hookEventName missing"
case "$sysmsg" in *"/dashboard"*) pass "P1d names /dashboard" ;; *) fail "P1d does not name /dashboard" ;; esac
case "$sysmsg" in *"dashboard_autostart"*) pass "P1e names the opt-in dashboard_autostart knob (full edition)" ;; *) fail "P1e does not name dashboard_autostart" ;; esac
case "$ctx" in *"emitted locally by a repo hook"*) pass "P1f model-facing copy is self-identifying (an unlabelled advisory is discounted as injection)" ;; *) fail "P1f model-facing copy is not self-identifying" ;; esac

# ── P2 / P3 ──────────────────────────────────────────────────────────────────
out="$(run "$SCRIPT" "$TMP/cfg")"; rc=$?
[ "$rc" = 0 ] && [ -z "$out" ] && pass "P2 silent once .ravenclaude/comfort-posture.yaml exists" || fail "P2 spoke in a configured project (rc=$rc, ${#out} bytes)"
out="$(run "$SCRIPT" "$TMP/empty" RC_DASHBOARD_PROMPT=off)"; rc=$?
[ "$rc" = 0 ] && [ -z "$out" ] && pass "P3 RC_DASHBOARD_PROMPT=off silences it" || fail "P3 spoke despite RC_DASHBOARD_PROMPT=off"

# ── P4: writes nothing ───────────────────────────────────────────────────────
before="$(find "$TMP/empty" "$TMP/home" -mindepth 1 2>/dev/null | wc -l | tr -d ' ')"
run "$SCRIPT" "$TMP/empty" >/dev/null
run "$SCRIPT" "$TMP/empty" >/dev/null
after="$(find "$TMP/empty" "$TMP/home" -mindepth 1 2>/dev/null | wc -l | tr -d ' ')"
[ "$before" = "$after" ] && [ "$after" = 0 ] && pass "P4 wrote nothing to the project or HOME across two runs" || fail "P4 files appeared (before=$before after=$after)"

# ── P5: edition wording ──────────────────────────────────────────────────────
out="$(run "$TMP/ed/scripts/dashboard-prompt.sh" "$TMP/empty")"
sysmsg_ed="$(printf '%s' "$out" | json_field systemMessage)"
case "$sysmsg_ed" in *"save my posture"*) pass "P5a no bin/rc beside it -> hosted-page paste-back wording" ;; *) fail "P5a edition wording missing 'save my posture'" ;; esac
case "$sysmsg_ed" in *"rc dashboard"* | *"dashboard_autostart"*) fail "P5b edition wording names rc/autostart, which the edition does not ship" ;; *) pass "P5b edition wording does not name rc dashboard or dashboard_autostart" ;; esac

# ── P6: fail-safe ────────────────────────────────────────────────────────────
out="$(run "$SCRIPT" "/nonexistent/zzz-$$")"; rc=$?
[ "$rc" = 0 ] && [ -z "$out" ] && pass "P6 nonexistent project dir -> exit 0, silent" || fail "P6 rc=$rc bytes=${#out}"

# ── P7: no-egress ────────────────────────────────────────────────────────────
leak_check() { # script -> 0 iff neither sentinel appears in the output
  local o
  o="$(run "$1" "$TMP/empty")"
  case "$o" in *PAYLOAD_SENTINEL_7f3a* | *ENV_SENTINEL_9c1d*) return 1 ;; esac
  [ -n "$o" ] # also require that it DID speak, or silence would pass vacuously
}
leak_check "$SCRIPT" && pass "P7 neither the stdin payload nor the environment is echoed (and it did speak)" || fail "P7 a sentinel leaked, or the hook was silent"

# ── P8: registered in both manifests ─────────────────────────────────────────
reg() { # manifest -> 0 iff a SessionStart startup|resume|clear|fork group runs dashboard-prompt.sh
  python3 - "$1" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
hooks = d.get("hooks", d)
for g in hooks.get("SessionStart", []):
    if g.get("matcher") == "startup|resume|clear|fork":
        for h in g.get("hooks", []):
            if "dashboard-prompt.sh" in h.get("command", ""):
                sys.exit(0)
sys.exit(1)
PY
}
reg plugins/ravenclaude-core/hooks/hooks.json && pass "P8a registered in hooks.json (consumers)" || fail "P8a not registered in hooks.json"
reg .claude/settings.json && pass "P8b registered in the dev-mirror .claude/settings.json" || fail "P8b not registered in .claude/settings.json"

# ── T1: teeth — remove the posture gate, a configured project must now hear it ─
grep -vF 'comfort-posture.yaml" ] && exit 0' "$SCRIPT" > "$TMP/mut-nogate.sh"
if [ "$(wc -l < "$TMP/mut-nogate.sh")" -lt "$(wc -l < "$SCRIPT")" ]; then
  out="$(run "$TMP/mut-nogate.sh" "$TMP/cfg")"
  [ -n "$out" ] && pass "T1 teeth: with the posture gate removed it speaks in a configured project (P2 depends on the gate)" || fail "T1 teeth: removing the gate did not change behaviour — P2 is vacuous"
else
  fail "T1 setup: could not locate the posture-gate line to remove"
fi

# ── T2: teeth — a mutant that echoes stdin must trip the P7 check ───────────
awk '{print} /^project_dir=/{print "cat"}' "$SCRIPT" > "$TMP/mut-echo.sh"
leak_check "$TMP/mut-echo.sh" && fail "T2 teeth: an echoing mutant passed P7 — the no-egress check is vacuous" || pass "T2 teeth: an echoing mutant is caught by the P7 check"

echo "dashboard-prompt: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
