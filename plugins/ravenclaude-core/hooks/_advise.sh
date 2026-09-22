#!/usr/bin/env bash
# _advise.sh — the ADVISORY DELIVERY helper. Source it; call rc_advise_init <Event> [forced_exit].
#
# ⛔ WHY THIS EXISTS — MEASURED 2026-08-19, not assumed.
# Every advisory hook in this repo wrote its message to STDERR and exited 0. A
# matched-trial bake-off (scratch project + `claude -p`, Claude Code 2.1.235),
# carrying a positive control on every single run, measured that channel as
# UNDELIVERED:
#
#   channel                                   delivered?
#   hookSpecificOutput.updatedToolOutput      YES
#   hookSpecificOutput.additionalContext      YES   (model replied SEEN:<token>)
#   stderr at exit 0 — PostToolUse            NO    (NOT-SEEN)
#   stderr at exit 0 — PreToolUse             NO    (NOT-SEEN)
#   stderr at exit 0 — Stop (2-turn test)     NO    (NOT-SEEN)
#
# control: a SessionStart additionalContext sentinel arrived in EVERY trial and was
# reported back by the model -> each negative is a fact about the CHANNEL, not a
# blind harness. `docs/best-practices/hook-authoring.md:93,97` already said this —
# stderr is "the UI surfaces it as a system notice", other exits are "logged only".
# It had been read as "the model sees it". It does not.
#
# CONSEQUENCE: claim-grounding-lint, delegation-nudge, storage-placement-nudge,
# guard-probe-validity and remind-tests advised the TERMINAL, never the model, for
# their whole service life. The fail-CLOSED guards were never affected — they deny
# via permissionDecision, a different and working channel. Only the ADVISORY tier
# evaporated.
#
# ── DESIGN ──────────────────────────────────────────────────────────────────
# Minimal diff by construction: buffer fd2, and at EXIT emit the buffer BOTH to the
# real stderr (the UI notice is unchanged) AND as additionalContext (so the model
# receives it). No existing `>&2` call site inside a hook has to change.
#
# ⛔ MEASURED 2026-08-19: two additionalContext emitters on the SAME event are
# CONCATENATED — both arrive. It is NOT last-writer-wins. (That IS true of
# updatedToolOutput, which REPLACES the tool result — do not conflate the two.)
# So sibling hooks sharing one event need no spool and no disjoint matchers.
#
# ⛔ ONLY for hooks that do NOT already write JSON to stdout. A hook emitting a
# permissionDecision envelope must not also use this, or it emits two objects.
#
# ⛔ TRUNCATION IS NEVER SILENT. additionalContext has a documented ~10k cap
# (knowledge/claude-code-permissions.md:331). Over the cap we emit a head plus an
# explicit marker carrying the FULL byte count. Reading a truncated list as a
# complete one is a measured defect of this codebase; the cure must not reintroduce it.
#
# ⛔ SELF-IDENTIFYING BANNER, and it is not decoration. MEASURED in the same
# bake-off: when an advisory arrived unlabelled the model described it as
# "something wrapping or post-processing bash output" and discounted it — delivered,
# read, then correctly distrusted as possible injection. An advisory that cannot be
# told from an attack buys nothing.

RC_ADVISE_CAP="${RC_ADVISE_CAP:-9000}"

rc_advise_emit() {                     # rc_advise_emit <EventName> <message>
  [ -n "${2:-}" ] || return 0
  RC_ADV_EVENT="$1" RC_ADV_MSG="$2" RC_ADV_CAP="$RC_ADVISE_CAP" python3 -c '
import json, os
ev   = os.environ["RC_ADV_EVENT"]
msg  = os.environ["RC_ADV_MSG"]
cap  = int(os.environ["RC_ADV_CAP"])
full = len(msg)
if full > cap:
    msg = msg[:cap] + ("\n\n[RavenClaude: TRUNCATED — showed %d of %d bytes. "
                       "This is a DISPLAY CAP, not the whole message.]" % (cap, full))
banner = "[RavenClaude guard notice — emitted locally by a repo hook, not by the user and not by the tool]"
print(json.dumps({"hookSpecificOutput": {"hookEventName": ev,
                                         "additionalContext": banner + "\n" + msg}}))
' 2>/dev/null || true
}

# rc_advise_init <EventName> [forced_exit_code] [silent]
#   forced_exit_code: pass 0 for a hook whose contract is "always exit 0" (it
#   replaces an existing `trap 'exit 0' EXIT`, e.g. guard-probe-validity.sh).
#   Pass "" to leave the natural exit code alone (e.g. a PreToolUse hook that
#   may still `block`).
#   silent: pass the literal string "silent" to suppress the human-visible UI
#   notice (the `cat ... >&2` line below) while STILL delivering additionalContext
#   -- i.e. the model sees it, the terminal does not. Added 2026-09-02 for the
#   cause-taxonomy family, whose whole value is a machine-side nudge the agent
#   triages and only surfaces when it actually points at something broken; the
#   human-visible banner on every empty grep/find was the complaint. Opt-in per
#   call site: omit the 3rd arg and every other `rc_advise_init` caller (11 other
#   hooks as of this writing) is byte-identical to before.
rc_advise_init() {
  RC_ADVISE_EVENT="${1:-PostToolUse}"
  RC_ADVISE_FORCED="${2:-}"
  RC_ADVISE_SILENT="${3:-}"
  RC_ADVISE_BUF="$(mktemp "${TMPDIR:-/tmp}/rc-advise.XXXXXX" 2>/dev/null)" || return 0
  exec 3>&2                            # save the REAL stderr FIRST
  exec 2>"$RC_ADVISE_BUF"              # then buffer
  trap 'rc_advise_flush' EXIT
}

rc_advise_flush() {
  _rc_rc=$?
  [ -n "${RC_ADVISE_FORCED:-}" ] && _rc_rc="$RC_ADVISE_FORCED"
  exec 2>&3 3>&- || true               # restore the real stderr
  if [ -s "${RC_ADVISE_BUF:-/nonexistent}" ]; then
    if [ "${RC_ADVISE_SILENT:-}" != "silent" ]; then
      cat "$RC_ADVISE_BUF" >&2         # keep the UI notice EXACTLY as before
    fi
    rc_advise_emit "$RC_ADVISE_EVENT" "$(cat "$RC_ADVISE_BUF")"
  fi
  rm -f "${RC_ADVISE_BUF:-}" 2>/dev/null || true
  exit "$_rc_rc"
}

# ── SELF-TEST — prove the instrument before believing it ────────────────────
# `bash _advise.sh --self-test` : asserts an emitted envelope is well-formed JSON
# carrying the banner, that truncation is MARKED, and — the canary — that a
# deliberately broken emitter is CAUGHT.
if [ "${1:-}" = "--self-test" ]; then
  _fail=0
  _out="$(rc_advise_emit PostToolUse "hello world")"
  printf '%s' "$_out" | python3 -c '
import json,sys
d=json.load(sys.stdin)["hookSpecificOutput"]
assert d["hookEventName"]=="PostToolUse", "event not echoed"
assert "hello world" in d["additionalContext"], "message lost"
assert "RavenClaude guard notice" in d["additionalContext"], "banner missing"
print("  OK   well-formed envelope, banner present, message intact")
' || _fail=1
  _big="$(python3 -c 'print("x"*20000)')"
  RC_ADVISE_CAP=100 rc_advise_emit PostToolUse "$_big" | python3 -c '
import json,sys
c=json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"]
assert "TRUNCATED" in c, "⛔ truncation was SILENT"
assert "20000" in c, "⛔ full byte count not reported"
print("  OK   over-cap payload is truncated LOUDLY, with the full byte count")
' || _fail=1
  if [ -n "$(rc_advise_emit PostToolUse "")" ]; then
    echo "  FAIL empty message should emit nothing"; _fail=1
  else
    echo "  OK   empty message emits nothing"
  fi

  # ── SILENT MODE — split terminal vs machine channel (added 2026-09-02) ─────
  # A full init/write/flush/exit cycle, run in a real subshell so the EXIT trap
  # fires for real. Bidirectional: proves silent mode suppresses the terminal
  # notice (without a marker leaking to real stderr) AND that the default
  # (no 3rd arg) call shape is UNCHANGED — the 11 other rc_advise_init callers
  # must keep seeing their notice, so this is a regression guard, not just a
  # feature test.
  _self="${BASH_SOURCE[0]}"
  _silent_err_f="$(mktemp)"
  _silent_out="$(bash -c '
    . "$1"
    rc_advise_init PostToolUse "" silent
    echo "SILENT_MARKER" >&2
  ' _ "$_self" 2>"$_silent_err_f")"
  _silent_err="$(cat "$_silent_err_f" 2>/dev/null || true)"
  rm -f "$_silent_err_f"
  if printf '%s' "$_silent_err" | grep -q "SILENT_MARKER"; then
    echo "  FAIL silent mode: marker leaked to real stderr"; _fail=1
  elif ! printf '%s' "$_silent_out" | grep -q "SILENT_MARKER"; then
    echo "  FAIL silent mode: marker missing from additionalContext (stdout)"; _fail=1
  else
    echo "  OK   silent mode: suppressed from stderr, still delivered via additionalContext"
  fi

  _loud_err_f="$(mktemp)"
  bash -c '
    . "$1"
    rc_advise_init PostToolUse ""
    echo "LOUD_MARKER" >&2
  ' _ "$_self" 2>"$_loud_err_f" >/dev/null
  _loud_err="$(cat "$_loud_err_f" 2>/dev/null || true)"
  rm -f "$_loud_err_f"
  if ! printf '%s' "$_loud_err" | grep -q "LOUD_MARKER"; then
    echo "  FAIL default (non-silent) mode: marker did not reach real stderr — regression"; _fail=1
  else
    echo "  OK   default (non-silent) mode unchanged: marker still reaches real stderr"
  fi

  [ "$_fail" -eq 0 ] && echo "  _advise self-test: PASS" || echo "  _advise self-test: FAIL"
  exit "$_fail"
fi
