#!/usr/bin/env bash
# test-guard-foreground-suite.sh — acceptance tests for hooks/guard-foreground-suite.sh
#
# The guard denies a FOREGROUND invocation of a long suite that cannot finish
# inside the Bash tool's hard 600000ms ceiling. Seven halves, and the ones that
# carry the weight are (d) and (f):
#
#   (a) must-pass — foreground full-suite invocations DENY (exit 2)
#   (b) must-pass — the two legitimate forms ALLOW: run_in_background, --check
#   (c) MENTION vs INVOCATION — grep/sed/git-show/wc that merely NAME the suite
#       must run. ⛔ A guard that cannot tell a command from a description of one
#       blocks its own repair; this repo has paid for that twice.
#   (d) MUST-FAIL — a neutered matcher must STOP denying, so (a) is measuring the
#       matcher and not the fixture. Carries its own vacuity control: if the
#       mutation does not apply, the half FAILS rather than passing green.
#   (e) the 600000ms clamp note appears when a caller asks for more — with the
#       under-ceiling control, so an unconditional note cannot pass as a working one
#   (f) the jq-free (python3) branch reaches the SAME verdicts — an untested
#       fallback that silently allows everything is the defect class this repo
#       keeps finding
#   (g) fail-open — no payload / unreadable payload ALLOWS. This is an ergonomic
#       guard, not a trust boundary; deny-on-unknown would be the worse failure.
#   (h) registration SCOPE — wired ONLY under PreToolUse + matcher "Bash", so the
#       two non-tool callers of the suite (CI's validate-marketplace.yml and
#       reset-plugin-cache.py's pre-atomic-swap verification, i.e. the Ragnarök
#       recovery path) stay structurally out of reach. ⛔ Pins the REGISTRATION,
#       not the matcher regex — widening the registration is the only way this
#       guard could ever reach recovery, and it is the thing a future edit would
#       change without noticing.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$(cd "$SCRIPT_DIR/.." && pwd)/guard-foreground-suite.sh"

PASS=0; FAIL=0
pass() { printf '  \033[32m✓\033[0m %s\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗\033[0m %s\n' "$1"; FAIL=$((FAIL + 1)); }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT INT TERM

# _j COMMAND [EXTRA_JSON] — build a PreToolUse payload. Fixture commands
# deliberately contain no double quotes or backslashes, so no escaping is needed.
_j() { printf '{"tool_name":"Bash","tool_input":{"command":"%s"%s}}' "$1" "${2:-}"; }

# _rc HOOKPATH JSON — drive a hook, return its exit code. Captured explicitly:
# ⛔ never `printf | grep -q` here — with pipefail a match SIGPIPEs the producer
# and 141 would be read as a verdict.
_rc() { printf '%s' "$2" | bash "$1" >/dev/null 2>&1; printf '%s' "$?"; }

_expect() { # $1 expected  $2 label  $3 json  [$4 hook override]
  local want="$1" label="$2" json="$3" hook="${4:-$HOOK}" got
  got="$(_rc "$hook" "$json")"
  if [ "$got" = "$want" ]; then pass "$label"; else fail "$label (expected $want, got $got)"; fi
}

echo
echo "── (a) foreground full-suite invocations must DENY ────────────────────────"
_expect 2 "plain foreground suite denies"        "$(_j 'bash scripts/audit-gates.sh')"
_expect 2 "cd && suite | tail denies"            "$(_j 'cd /x && bash scripts/audit-gates.sh 2>&1 | tail -5')"
_expect 2 "direct ./scripts execution denies"    "$(_j './scripts/audit-gates.sh')"
_expect 2 "env prefix + redirect denies"         "$(_j 'export PATH=x; bash plugins/../scripts/audit-gates.sh > /tmp/o 2>&1')"

echo
echo "── (b) the legitimate forms must ALLOW ────────────────────────────────────"
_expect 0 "run_in_background:true allows"        "$(_j 'bash scripts/audit-gates.sh' ',"run_in_background":true')"
_expect 0 "--check N single gate allows"         "$(_j 'bash scripts/audit-gates.sh --check 140')"
_expect 0 "explicit ACK escape allows"           "$(_j 'RC_SUITE_FOREGROUND_ACK=1 bash scripts/audit-gates.sh')"
_expect 0 "unrelated command allows"             "$(_j 'ls -la')"

echo
echo "── (c) a MENTION is not an INVOCATION ─────────────────────────────────────"
_expect 0 "grep naming the suite allows"         "$(_j 'grep -n needle scripts/audit-gates.sh')"
_expect 0 "sed naming the suite allows"          "$(_j 'sed -n 1,60p scripts/audit-gates.sh')"
_expect 0 "git show naming the suite allows"     "$(_j 'git show HEAD:scripts/audit-gates.sh')"
_expect 0 "wc naming the suite allows"           "$(_j 'wc -l scripts/audit-gates.sh')"

echo
echo "── (d) MUST-FAIL: a neutered matcher must stop denying ────────────────────"
# ⛔ THE VACUITY CONTROL COMES FIRST. If the mutation silently fails to apply,
# the mutant is byte-identical to the shipped hook, it denies exactly as the real
# one does, and a naive half would report that as proof of teeth. Assert the
# files DIFFER before drawing any conclusion from the mutant's behaviour.
MUTANT="$TMP/mutant.sh"
sed 's/^\[ "\$_gfs_hit" = "1" \] || exit 0$/exit 0  # NEUTERED BY THE MUST-FAIL HALF/' "$HOOK" > "$MUTANT"
if cmp -s "$HOOK" "$MUTANT"; then
  fail "(d) mutation did not apply — this half is VACUOUS, not green"
elif ! bash -n "$MUTANT" 2>/dev/null; then
  fail "(d) mutant is not valid bash — the half cannot measure anything"
else
  pass "(d) control: the mutation applied and the mutant parses"
  _expect 0 "(d) neutered matcher stops denying, so (a) measures the matcher" \
    "$(_j 'bash scripts/audit-gates.sh')" "$MUTANT"
fi

echo
echo "── (e) the 600000ms clamp note ────────────────────────────────────────────"
_msg="$(printf '%s' "$(_j 'bash scripts/audit-gates.sh' ',"timeout":900000')" | bash "$HOOK" 2>&1 >/dev/null || true)"
case "$_msg" in
  *"silently clamped"*) pass "(e) an over-ceiling timeout is called out as clamped" ;;
  *) fail "(e) no clamp note for timeout=900000" ;;
esac
_msg2="$(printf '%s' "$(_j 'bash scripts/audit-gates.sh' ',"timeout":60000')" | bash "$HOOK" 2>&1 >/dev/null || true)"
case "$_msg2" in
  *"silently clamped"*) fail "(e) clamp note fired for an UNDER-ceiling timeout — the note is unconditional" ;;
  *) pass "(e) control: no clamp note for an under-ceiling timeout" ;;
esac

echo
echo "── (f) the jq-free (python3) branch reaches the same verdicts ─────────────"
NOJQ="$TMP/nojq"; mkdir -p "$NOJQ"
for _b in bash sed awk printf basename dirname python3 cat cmp mktemp rm; do
  _p="$(command -v "$_b" 2>/dev/null)" && ln -sf "$_p" "$NOJQ/$_b"
done
if PATH="$NOJQ" command -v jq >/dev/null 2>&1; then
  fail "(f) jq is still reachable — this half cannot test the fallback"
else
  pass "(f) control: jq is absent from the stripped PATH"
  _g="$(printf '%s' "$(_j 'bash scripts/audit-gates.sh')" | PATH="$NOJQ" bash "$HOOK" >/dev/null 2>&1; printf '%s' "$?")"
  if [ "$_g" = "2" ]; then pass "(f) jq-free: foreground suite still denies"; else fail "(f) jq-free: expected 2, got $_g"; fi
  _g="$(printf '%s' "$(_j 'grep -n needle scripts/audit-gates.sh')" | PATH="$NOJQ" bash "$HOOK" >/dev/null 2>&1; printf '%s' "$?")"
  if [ "$_g" = "0" ]; then pass "(f) jq-free: a mention still allows"; else fail "(f) jq-free: expected 0, got $_g"; fi
fi

echo
echo "── (g) fail-open on no / unreadable payload ───────────────────────────────"
_g="$(printf '' | bash "$HOOK" >/dev/null 2>&1; printf '%s' "$?")"
if [ "$_g" = "0" ]; then pass "(g) empty stdin allows"; else fail "(g) empty stdin: expected 0, got $_g"; fi
_g="$(printf 'not json at all' | bash "$HOOK" >/dev/null 2>&1; printf '%s' "$?")"
if [ "$_g" = "0" ]; then pass "(g) unparseable payload allows"; else fail "(g) unparseable payload: expected 0, got $_g"; fi
_g="$(bash "$HOOK" < /dev/null >/dev/null 2>&1; printf '%s' "$?")"
if [ "$_g" = "0" ]; then pass "(g) /dev/null stdin allows"; else fail "(g) /dev/null stdin: expected 0, got $_g"; fi

echo
echo "── (h) registration SCOPE — the guard must not be able to reach CI or recovery ─"
# ⛔ THIS IS THE HALF THAT PROTECTS DISASTER RECOVERY, and it asserts a REGISTRATION
# property rather than a matcher one, because the matcher is not what keeps the guard
# out of those paths.
#
# The suite is also invoked by two callers that never go through the Bash TOOL:
#   .github/workflows/validate-marketplace.yml:392  `run: scripts/audit-gates.sh`
#   scripts/reset-plugin-cache.py:134               subprocess, to verify the fresh
#                                                   tree BEFORE the atomic swap
# The second is the Ragnarök recovery path. A guard that reached it would fail the
# verification step and break recovery in a way nobody would find until they needed
# it — the worst possible time. A PreToolUse(Bash) hook is structurally unable to
# reach either, since neither is a Claude Code tool call. But "structurally" is only
# true while the registration stays narrow, so pin the registration itself: if anyone
# later widens the matcher (to `*`, or adds a PreToolUse group with no matcher), this
# half fails and says why.
HOOKS_JSON="$(cd "$SCRIPT_DIR/.." && pwd)/hooks.json"
if [ ! -f "$HOOKS_JSON" ]; then
  fail "(h) hooks.json not found at $HOOKS_JSON — cannot verify registration scope"
elif ! command -v python3 >/dev/null 2>&1; then
  fail "(h) python3 absent — cannot parse hooks.json to verify registration scope"
else
  _scope="$(python3 - "$HOOKS_JSON" <<'PY'
import json, sys
doc = json.load(open(sys.argv[1]))
hooks = doc.get("hooks", doc)
target = "guard-foreground-suite.sh"
placements = []
for event, groups in hooks.items():
    if not isinstance(groups, list):
        continue
    for g in groups:
        for h in (g.get("hooks") or []):
            if target in (h.get("command") or ""):
                placements.append((event, g.get("matcher")))
if not placements:
    print("ABSENT")
elif len(placements) != 1:
    print("MULTIPLE:" + repr(placements))
else:
    event, matcher = placements[0]
    print("%s|%s" % (event, matcher))
PY
)" || _scope="ERROR"
  case "$_scope" in
    "PreToolUse|Bash")
      pass "(h) wired exactly once, PreToolUse + matcher 'Bash' — CI and reset-plugin-cache are out of reach" ;;
    ABSENT)
      fail "(h) the hook is NOT registered in hooks.json — it would never fire at all" ;;
    MULTIPLE:*)
      fail "(h) registered more than once: $_scope — scope is no longer narrow" ;;
    PreToolUse\|*)
      fail "(h) PreToolUse but matcher is '${_scope#PreToolUse|}', not 'Bash' — a widened matcher can reach non-Bash tool calls" ;;
    *)
      fail "(h) unexpected registration scope: $_scope" ;;
  esac
fi

echo
printf '  %s pass, %s fail\n' "$PASS" "$FAIL"
[ "$FAIL" -eq 0 ] || exit 1
