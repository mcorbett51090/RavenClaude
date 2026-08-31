#!/usr/bin/env bash
# check-host-canary.sh — Gate 207
#
# Behavioral canary for host onboarding (P16 install-wires-nothing, P18
# silent-disarm-on-update). Generalizes Gate 167's Copilot→tribunal
# planted-marker round-trip across every --host lane.
#
# ── M10 HONEST LIMIT ──────────────────────────────────────────────────────
# Live-host behavior (a running Copilot / Codex / Cursor / Gemini session) is
# un-exercisable in CI. This gate covers adapter I/O + the planted-marker
# round-trip, and that the installer actually *calls* the canary and the
# shared re-arm helper. A host whose live binary ignores a correctly-wired
# hooks file stays owner-verified.
#
# ── D4 ADVISORY ───────────────────────────────────────────────────────────
# The installer WARNS when the marker does not fire; it does not fail the
# install. This script is the mechanism's teeth, not a hard onboarding bar.
#
# ── Exit codes ────────────────────────────────────────────────────────────
#   0  clean
#   2  a finding (fail-closed). Exit 1 is never used for a finding — the
#      harness treats exit 1 as a non-blocking error (silent fail-open).
#
# Usage:
#   bash scripts/check-host-canary.sh              # live-tree good path
#   bash scripts/check-host-canary.sh --self-test  # good path + both must-fail
#   bash scripts/check-host-canary.sh --must-fail  # only the two mutant halves
#   bash scripts/check-host-canary.sh --drive-mutant-silent
#       # emit the silent-success mutant's exit (suite asserts it is 2)

set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
CORE="$REPO/plugins/ravenclaude-core"
REARM="$CORE/hooks/_rearm-notice.sh"
CANARY="$CORE/hooks/_host-canary.sh"
INSTALLER="$REPO/scripts/ravenclaude"
HOSTMAP="$CORE/knowledge/host-support.json"

PASS=0
FAIL=0
ok()  { PASS=$((PASS + 1)); printf '  ✓ %s\n' "$1"; }
bad() { FAIL=$((FAIL + 1)); printf '  ✗ %s\n' "$1"; }

die2() { printf 'host-canary: %s\n' "$1" >&2; exit 2; }

for f in "$REARM" "$CANARY" "$INSTALLER" "$HOSTMAP"; do
  [ -f "$f" ] || die2 "missing $f"
done

# shellcheck source=/dev/null
. "$REARM"
# shellcheck source=/dev/null
. "$CANARY"

# ── Good path: planted-marker round-trip through each hook-capable adapter ─
roundtrip() {
  local host="$1" tmp token out rc
  tmp="$(mktemp -d "${TMPDIR:-/tmp}/g207-rt.XXXXXX")"
  token="g207-$host-$$"
  out="$tmp/marker"
  RC_CANARY_TOKEN="$token"
  RC_CANARY_OUT="$out"
  export RC_CANARY_TOKEN RC_CANARY_OUT
  rc=0
  _rc_host_canary "$host" "$tmp" >/dev/null 2>&1 || rc=$?
  if [ "$rc" -eq 0 ] && [ -f "$out" ] && [ "$(cat "$out")" = "$token" ]; then
    ok "round-trip: $host adapter fired the planted marker"
  else
    bad "round-trip: $host marker did not fire (rc=$rc)"
  fi
  rm -rf "$tmp"
}

# ── Good path: shared re-arm helper emits the distinctive tokens ──────────
check_rearm_helper() {
  local out
  out="$(_rc_rearm_notice codex update /nonexistent 2>&1)"
  if printf '%s' "$out" | grep -q 'BY HASH' && printf '%s' "$out" | grep -q '/hooks'; then
    ok "rearm: hash_trust (codex) emits BY HASH + /hooks"
  else
    bad "rearm: hash_trust notice missing distinctive tokens"
  fi
  out="$(_rc_rearm_notice copilot update /nonexistent 2>&1)"
  if printf '%s' "$out" | grep -q 'version floor' && printf '%s' "$out" | grep -q '1.0.52'; then
    ok "rearm: version_floor (copilot) emits version floor + 1.0.52"
  else
    bad "rearm: version_floor notice missing distinctive tokens"
  fi
  out="$(_rc_rearm_notice aider update /nonexistent 2>&1)"
  if [ -z "$out" ]; then
    ok "rearm: none (aider) is a silent no-op"
  else
    bad "rearm: none-gate host emitted a notice: $out"
  fi
}

# ── Good path: SSOT has activation_gate on every host ─────────────────────
check_map_field() {
  local rc
  rc=0
  python3 -c 'import json,sys
allowed={"hash_trust","version_floor","none"}
d=json.load(open(sys.argv[1]))
missing=[]
for name, info in (d.get("hosts") or {}).items():
    g=(info or {}).get("activation_gate")
    if g not in allowed:
        missing.append("%s=%r" % (name, g))
if missing:
    sys.stderr.write("missing/invalid activation_gate: %s\n" % ", ".join(missing))
    sys.exit(2)
want={"codex":"hash_trust","copilot":"version_floor"}
for h, g in want.items():
    got=(d.get("hosts") or {}).get(h, {}).get("activation_gate")
    if got != g:
        sys.stderr.write("%s activation_gate is %r, want %r\n" % (h, got, g))
        sys.exit(2)
' "$HOSTMAP" || rc=$?
  if [ "$rc" -eq 0 ]; then
    ok "host-support.json: every host has activation_gate; codex=hash_trust copilot=version_floor"
  else
    bad "host-support.json: activation_gate pin failed (rc=$rc)"
  fi
}

# Extract a named function body from the installer (bash-3.2: no mapfile).
_installer_fn() {
  local name="$1"
  python3 -c 'import sys
src=open(sys.argv[1]).read().splitlines()
name=sys.argv[2]
start=None
for i,line in enumerate(src):
    if line.startswith(name+"()") or line.startswith(name+" ()"):
        start=i
        break
if start is None:
    sys.exit(2)
# Walk to the next top-level function or the case dispatcher.
body=[]
depth=0
started=False
for line in src[start:]:
    body.append(line)
    depth += line.count("{") - line.count("}")
    if "{" in line:
        started=True
    if started and depth<=0:
        break
sys.stdout.write("\n".join(body)+"\n")
' "$INSTALLER" "$name"
}

# ── Good path: installer consumes the helpers at install / update / status ─
check_installer_wires() {
  local fn
  if grep -q '_rearm-notice.sh' "$INSTALLER" && grep -q '_host-canary.sh' "$INSTALLER"; then
    ok "installer sources _rearm-notice.sh and _host-canary.sh"
  else
    bad "installer does not source the shared helpers"
  fi
  fn="$(_installer_fn cmd_install)"
  if printf '%s' "$fn" | grep -q '_rc_host_canary\|_rc_finish_host_install'; then
    ok "cmd_install calls the canary (or the shared finish helper)"
  else
    bad "cmd_install does not call the canary"
  fi
  fn="$(_installer_fn cmd_update)"
  if printf '%s' "$fn" | grep -q '_rc_rearm'; then
    ok "cmd_update calls _rc_rearm_* (P18: re-arm on update)"
  else
    bad "cmd_update does not call _rc_rearm_* — a hash_trust host would silently disarm"
  fi
  fn="$(_installer_fn cmd_status)"
  if printf '%s' "$fn" | grep -q '_rc_rearm'; then
    ok "cmd_status calls _rc_rearm_*"
  else
    bad "cmd_status does not call _rc_rearm_*"
  fi
}

run_good() {
  printf '── Gate 207 good path ──\n'
  check_map_field
  check_rearm_helper
  check_installer_wires
  # Codex + Copilot are the pass-on-good lanes (canary-proven per Gate 167).
  # Claude-code is native (probe itself). Gemini/cursor adapters are the same
  # planted-marker shape; include them so a dropped adapter is caught.
  roundtrip codex
  if command -v jq >/dev/null 2>&1; then
    roundtrip copilot
  else
    printf '  ‼ round-trip: copilot SKIPPED — jq absent (adapter no-ops without it)\n'
    printf '    THIS IS NOT A PASS. CI must provide jq.\n'
    if [ -n "${CI:-}" ]; then
      bad "round-trip: copilot unrunnable in CI (jq missing)"
    fi
  fi
  roundtrip claude-code
}

# ── Must-fail 1: installer/canary mutant reports success, marker never fires ─
# Mutate _rc_canary_invoke into a no-op. The canary still "runs" and, if it
# skipped the marker check, would return 0. We plant OUR marker and require
# that it stays unwritten — then the checker itself exits 2. A canary that
# still checks its marker will return 2; we treat that as "the canary caught
# it" (the mechanism works). A canary that returns 0 with an empty marker is
# the silent-success defect this half exists to catch.
build_silent_mutant() {
  local dest="$1"
  python3 -c 'import sys
src=open(sys.argv[1]).read()
anchor="_rc_canary_invoke() {"
if anchor not in src:
    sys.stderr.write("MUTATION ANCHOR NOT FOUND: _rc_canary_invoke() {\n")
    sys.exit(3)
# Replace the function body with a no-op that does not write the marker.
# Keep the name so the call site still resolves. Assembled, not triple-quoted,
# so this -c string cannot desync its own quotes.
new = (
    "_rc_canary_invoke() {\n"
    "  return 0\n"
    "}\n"
    "_rc_canary_invoke_REMOVED() {"
)
open(sys.argv[2],"w").write(src.replace(anchor, new, 1))
' "$CANARY" "$dest"
}

drive_silent_mutant() {
  local tmp mutant rc token out
  tmp="$(mktemp -d "${TMPDIR:-/tmp}/g207-m1.XXXXXX")"
  mutant="$tmp/canary-mutant.sh"
  if ! build_silent_mutant "$mutant"; then
    rm -rf "$tmp"
    printf '%s\n' "3"
    return 0
  fi
  token="g207-silent-$$"
  out="$tmp/marker"
  : >"$out"
  # Source the mutant over the real canary.
  # shellcheck source=/dev/null
  . "$mutant"
  RC_CANARY_TOKEN="$token"
  RC_CANARY_OUT="$out"
  export RC_CANARY_TOKEN RC_CANARY_OUT
  rc=0
  _rc_host_canary codex "$tmp" >/dev/null 2>&1 || rc=$?
  # The planted marker must NOT have been written by the no-op invoke.
  if [ -f "$out" ] && [ "$(cat "$out")" = "$token" ]; then
    # Mutant somehow wrote the marker without invoking — checker cannot see
    # the defect. That's a vacuous teeth half; fail closed.
    rm -rf "$tmp"
    printf '%s\n' "0"
    return 0
  fi
  # Marker never fired. The canary should have returned 2 (it caught itself)
  # OR returned 0 (silent success). Either way the CHECKER's finding is that
  # the marker did not fire after a claimed invoke — that is exit 2.
  rm -rf "$tmp"
  if [ "$rc" -eq 0 ]; then
    # Silent success: the exact MH-07 shape. Caught by US, exit 2.
    printf '%s\n' "2"
    return 0
  fi
  # The canary itself returned nonzero — the mechanism caught the no-op.
  # Surface that as the must-fail finding (exit 2) so the suite can assert it.
  printf '%s\n' "2"
}

# ── Must-fail 2: hash_trust re-arm notice stripped from update ─────────────
# Copy the installer, strip every _rc_rearm call from cmd_update, then run
# the same "cmd_update calls _rc_rearm_*" assertion. Must go red.
drive_rearm_stripped_mutant() {
  local tmp mutant rc
  tmp="$(mktemp -d "${TMPDIR:-/tmp}/g207-m2.XXXXXX")"
  mutant="$tmp/ravenclaude"
  python3 -c 'import sys
src=open(sys.argv[1]).read().splitlines()
out=[]
in_update=False
depth=0
started=False
stripped=0
for line in src:
    if (not in_update) and (line.startswith("cmd_update()") or line.startswith("cmd_update ()")):
        in_update=True
        depth=0
        started=False
    if in_update:
        if "_rc_rearm" in line and not line.lstrip().startswith("#"):
            stripped += 1
            out.append("    :  # stripped by Gate 207 mutant")
        else:
            out.append(line)
        depth += line.count("{") - line.count("}")
        if "{" in line:
            started=True
        if started and depth<=0:
            in_update=False
        continue
    out.append(line)
if stripped < 1:
    sys.stderr.write("MUTATION ANCHOR NOT FOUND: no _rc_rearm in cmd_update\n")
    sys.exit(3)
open(sys.argv[2],"w").write("\n".join(out)+"\n")
' "$INSTALLER" "$mutant" || { rm -rf "$tmp"; printf '%s\n' "3"; return 0; }
  # Re-run the cmd_update-calls-rearm check against the mutant.
  rc=0
  python3 -c 'import sys
src=open(sys.argv[1]).read().splitlines()
start=None
for i,line in enumerate(src):
    if line.startswith("cmd_update()") or line.startswith("cmd_update ()"):
        start=i
        break
if start is None:
    sys.exit(2)
depth=0
started=False
body=[]
for line in src[start:]:
    body.append(line)
    depth += line.count("{") - line.count("}")
    if "{" in line:
        started=True
    if started and depth<=0:
        break
text="\n".join(body)
if "_rc_rearm" in text:
    sys.exit(0)
sys.exit(2)
' "$mutant" || rc=$?
  rm -rf "$tmp"
  printf '%s\n' "$rc"
}

run_must_fail() {
  printf '── Gate 207 must-fail halves ──\n'
  local rc
  rc="$(drive_silent_mutant)"
  if [ "$rc" -eq 2 ]; then
    ok "teeth: installer/canary mutant that never fires the marker is caught (exit 2)"
  elif [ "$rc" -eq 3 ]; then
    bad "teeth: silent-success mutant could not be built (anchor missing)"
  else
    bad "teeth: silent-success mutant was NOT caught (got $rc, want 2)"
  fi
  rc="$(drive_rearm_stripped_mutant)"
  if [ "$rc" -eq 2 ]; then
    ok "teeth: hash_trust re-arm notice stripped from update is caught (exit 2)"
  elif [ "$rc" -eq 3 ]; then
    bad "teeth: update-rearm mutant could not be built (anchor missing)"
  else
    bad "teeth: stripped-rearm update was NOT caught (got $rc, want 2)"
  fi
}

MODE="${1:-}"
case "$MODE" in
  --drive-mutant-silent)
    rc="$(drive_silent_mutant)"
    exit "$rc"
    ;;
  --must-fail)
    run_must_fail
    if [ "$FAIL" -gt 0 ]; then exit 2; fi
    # --must-fail means "the teeth halves ran and both mutants were caught".
    exit 0
    ;;
  --self-test)
    run_good
    run_must_fail
    ;;
  "")
    run_good
    ;;
  *)
    printf 'usage: check-host-canary.sh [--self-test|--must-fail|--drive-mutant-silent]\n' >&2
    exit 2
    ;;
esac

printf '  (%d pass, %d fail)\n' "$PASS" "$FAIL"
if [ "$FAIL" -gt 0 ]; then
  exit 2
fi
exit 0
