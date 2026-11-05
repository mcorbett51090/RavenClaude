#!/usr/bin/env bash
# dod-gate.sh — Stop-hook definition-of-done gate.
#
# Closes the "hallucinating" gap that command review cannot: it gates work
# CORRECTNESS, not command safety. If source files changed this session AND a
# `definition_of_done.cmd` is configured in .ravenclaude/comfort-posture.yaml,
# it runs that command (tests / build / lint) when the agent tries to STOP and
# BLOCKS the stop until the command passes — so "looks done" becomes "is done"
# without the human being the verification loop (Anthropic best-practices Layer 5).
#
# Self-limited: blocks at most `max_blocks` (default 8) consecutive times per
# session, then force-allows with a warning — Claude Code force-overrides Stop
# after 8, but Copilot CLI has no such guarantee, so the cap must be ours.
# The first-run trust refusal counts toward the same cap. It used to exit 2
# on every Stop without advancing the counter, and Copilot turns that block
# reason into the next user prompt. A reason that does not say NOT DONE or
# STOP makes the agent ask whether the work is finished, then stop again.
#
# Verdicts the agent is allowed to act on (the reason text, nothing else):
#   VERDICT: NOT DONE — one [FAIL] line. Do that, then stop again. Do not ask.
#   VERDICT: STOP     — max_blocks reached. End the turn. Do not ask.
#   no verdict line   — this hook allowed the stop. That is DONE.
#
# No `definition_of_done.cmd` configured -> exit 0 (the advisory remind-tests.sh
# nudge still fires). No posture file -> zero cost. Deterministic: the gate is a
# command's exit code, no model in the loop, so it ports to Copilot unchanged via
# the adapter's `stop` mode. Config:
#   definition_of_done:
#     cmd: "npm test && npm run lint"
#     max_blocks: 8

set -uo pipefail

# Structured hook-event substrate (P0.2). Sourced fail-safe — a missing helper
# becomes a no-op so the emit calls below can never throw or block the verdict.
_emit_event_helper="$(dirname "$0")/_emit-event.sh"
if [ -f "$_emit_event_helper" ]; then
  # shellcheck source=/dev/null
  . "$_emit_event_helper" 2>/dev/null || true
fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

payload=""
[ ! -t 0 ] && payload="$(cat)"
cwd="$PWD"
sid="stop"
if command -v jq >/dev/null 2>&1 && [ -n "$payload" ]; then
  c="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null)"; [ -n "$c" ] && cwd="$c"
  s="$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null)"; [ -n "$s" ] && sid="$s"
fi
# SH-F4 (2026-10-06): posture + state are project/worktree-scoped. Payload cwd
# may be a subdirectory after `cd`. Walk up from that cwd for `.ravenclaude/`
# FIRST (preserves per-worktree isolation), then fall back to CLAUDE_PROJECT_DIR
# (SessionStart / adapters), else keep the payload cwd.
_payload_cwd="$cwd"
# A RELATIVE payload cwd (the Copilot adapter supplies "." when both .cwd and
# .workspaceRoot were omitted) makes the walk-up below spin forever: `dirname .`
# is `.`, a fixed point that is neither empty nor "/". Resolve a relative cwd to
# absolute first, and break on a fixed point (belt-and-suspenders). [1b-1]
case "$_payload_cwd" in
  /*) : ;;
  *) _payload_cwd="$(cd "$_payload_cwd" 2>/dev/null && pwd)" || _payload_cwd="$PWD" ;;
esac
[ -n "$_payload_cwd" ] || _payload_cwd="$PWD"
root=""
_d="$_payload_cwd"
while [ -n "$_d" ] && [ "$_d" != "/" ]; do
  if [ -d "${_d}/.ravenclaude" ]; then
    root="$_d"
    break
  fi
  _p="$(dirname "$_d")"
  [ "$_p" = "$_d" ] && break
  _d="$_p"
done
if [ -z "$root" ] && [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -d "${CLAUDE_PROJECT_DIR}/.ravenclaude" ]; then
  root="$CLAUDE_PROJECT_DIR"
fi
[ -n "$root" ] || root="$_payload_cwd"
cwd="$root"

posture="${cwd}/.ravenclaude/comfort-posture.yaml"
[ -f "$posture" ] || exit 0
# Vendored PyYAML fallback dir (stock macOS python3 has no PyYAML) — passed as argv[2]
# to each snippet below, which APPENDS it so an installed PyYAML still wins.
_yaml_vendor="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." 2>/dev/null && pwd)/scripts/vendor"

# Pull definition_of_done.cmd + max_blocks (PyYAML with a tolerant fallback).
# Python read into a var + run via `python3 -c`, NOT a heredoc nested in `$()`
# (bash 3.2 mis-parses that nesting — see guard-destructive.sh + the
# audit-gates no-heredoc-in-cmd-substitution gate). read -d '' returns non-zero at EOF.
IFS= read -r -d '' __DOD_CMD_PY <<'PY' || true
import sys
if len(sys.argv) > 2: sys.path.append(sys.argv[2])  # vendored PyYAML fallback
try:
    import yaml; d = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
except Exception:
    d = {}
dod = d.get("definition_of_done") or {}
print(dod.get("cmd","") if isinstance(dod, dict) else "")
PY
dod_cmd="$(python3 -c "$__DOD_CMD_PY" "$posture" "$_yaml_vendor" 2>/dev/null || true)"
IFS= read -r -d '' __MAX_BLOCKS_PY <<'PY' || true
import sys
if len(sys.argv) > 2: sys.path.append(sys.argv[2])  # vendored PyYAML fallback
try:
    import yaml; d = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
except Exception:
    d = {}
dod = d.get("definition_of_done") or {}
mb = dod.get("max_blocks", 8) if isinstance(dod, dict) else 8
try: mb = int(mb)
except Exception: mb = 8
print(mb)
PY
max_blocks="$(python3 -c "$__MAX_BLOCKS_PY" "$posture" "$_yaml_vendor" 2>/dev/null || echo 8)"
[ -z "$dod_cmd" ] && exit 0    # no DoD configured -> advisory remind-tests handles the nudge
case "$max_blocks" in (*[!0-9]*|"") max_blocks=8;; esac

# Only gate if source actually changed this session (mirror remind-tests' filter).
# Use --porcelain=v1 -z: the NUL-delimited form emits each path as a RAW, UNQUOTED
# record (porcelain v1's default quotes/space-splits paths, so the prior awk `$2`
# field-parse silently missed any changed file with a space in its name, and split
# rename `old -> new` lines — under-counting to 0 and skipping the gate entirely).
# grep -c matches the extension as a whole-line suffix (not a fixed field), so
# spaces in the path are irrelevant; -z rename records emit old+new as separate
# raw records, both scanned — we only need whether ANY changed path is source.
code_changed="$(git -C "$cwd" status --porcelain=v1 -z 2>/dev/null \
  | tr '\0' '\n' \
  | grep -cE '\.(ts|tsx|js|jsx|mjs|cjs|py|go|rs|java|kt|rb|php|cs|swift|scala)$')" || true
[ "${code_changed:-0}" -eq 0 ] && exit 0

safe_sid="$(printf '%s' "$sid" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
[ -z "$safe_sid" ] && safe_sid="stop"
bdir="${cwd}/.ravenclaude/runs/thing/dod"
mkdir -p "$bdir" 2>/dev/null || true
bf="${bdir}/${safe_sid}"
blocks=0
[ -r "$bf" ] && blocks="$(cat "$bf" 2>/dev/null || echo 0)"
case "$blocks" in (*[!0-9]*|"") blocks=0;; esac

# Copilot injects a Stop block reason as the next user prompt. These shapes
# are the whole stop rule.
_dod_not_done() {
  local why="$1"
  local detail="${2:-}"
  cat <<EOF
VERDICT: NOT DONE
Stop rule: do not ask if the work is done. Do not end the turn. Do the single [FAIL] line, then stop again. If the next stop is not blocked, the verdict is DONE — end the turn and do not re-ask.

Checklist:
- [FAIL] ${why}
- [PASS] the definition-of-done command exits 0
- [DONE] only when every line is PASS

${detail}
EOF
}

_dod_bump_block() {
  blocks=$((blocks + 1))
  printf '%s' "$blocks" > "$bf" 2>/dev/null || true
}

_dod_force_stop() {
  local why="$1"
  rm -f "$bf" 2>/dev/null || true
  cat >&2 <<EOF
VERDICT: STOP
The definition-of-done gate is releasing this turn after ${blocks} blocks (${why}).
Checklist:
- [FAIL] the gate command has not exited 0, or it was not authorized
- [DONE] you stop now anyway
Stop rule: end the turn. Tell the user the gate did not pass. Do not ask if the work is done. Do not start another check.
EOF
  exit 0
}

# ── First-run trust gate (closes Codex desktop trust review Finding 1) ──────
# $dod_cmd is shell-executed via `bash -c` below, but it came from a YAML field
# (definition_of_done.cmd) that a malicious PR could edit. Before the very first
# run per session per cmd value, refuse to execute and surface the literal cmd
# plus the `touch <path>` authorization step. After the user/agent touches the
# confirm file, this gate is silent for the rest of the session for this cmd.
# Rotating the YAML cmd re-triggers (hash mismatch); a new session re-triggers
# (safe_sid in path). Set `definition_of_done.trusted: true` in posture YAML
# to skip the gate entirely (you've reviewed the YAML and accept silent exec).
IFS= read -r -d '' __DOD_TRUSTED_PY <<'PY' || true
import sys
if len(sys.argv) > 2: sys.path.append(sys.argv[2])  # vendored PyYAML fallback
try:
    import yaml
    d = yaml.safe_load(open(sys.argv[1], encoding="utf-8")) or {}
except Exception:
    d = {}
dod = d.get("definition_of_done") or {}
print("true" if (isinstance(dod, dict) and dod.get("trusted") is True) else "false")
PY
dod_trusted="$(python3 -c "$__DOD_TRUSTED_PY" "$posture" "$_yaml_vendor" 2>/dev/null || echo "false")"

# ── Sever the trust self-attestation (b26-dodgate-cmd-exec-trusted-bypass) ──
# `trusted: true` and `cmd` both live in the SAME attacker-writable YAML file, so a
# single malicious PR/commit can set both at once — the YAML declaring its own cmd
# "reviewed" with nothing to distinguish that from an untrusted first-run. Honor
# `trusted: true` only when git shows the `trusted:` line was last touched in a
# DIFFERENT commit than the `cmd:` line — i.e. trust was granted as a genuinely
# separate act, not alongside the payload it is trusting. Any ambiguity (no git,
# untracked/dirty file with both lines uncommitted, unresolvable blame) fails SAFE:
# `dod_trusted` is forced back to "false" and the confirm-file challenge below still
# runs. This directly defeats the finding's stated trigger (one commit setting both
# fields) without touching the confirm-file mechanism itself.
if [ "$dod_trusted" = "true" ] && command -v git >/dev/null 2>&1 \
  && git -C "$cwd" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  dod_trust_sep=""
  trusted_line="$(grep -n -m1 -E '^[[:space:]]*trusted:[[:space:]]*true[[:space:]]*$' "$posture" 2>/dev/null | cut -d: -f1)"
  cmd_line="$(grep -n -m1 -E '^[[:space:]]*cmd:' "$posture" 2>/dev/null | cut -d: -f1)"
  if [ -n "$trusted_line" ] && [ -n "$cmd_line" ]; then
    trusted_commit="$(git -C "$cwd" blame -L "${trusted_line},${trusted_line}" --porcelain -- "$posture" 2>/dev/null | head -1 | awk '{print $1}')"
    cmd_commit="$(git -C "$cwd" blame -L "${cmd_line},${cmd_line}" --porcelain -- "$posture" 2>/dev/null | head -1 | awk '{print $1}')"
    if [ -n "$trusted_commit" ] && [ -n "$cmd_commit" ] && [ "$trusted_commit" != "$cmd_commit" ]; then
      dod_trust_sep="true"
    fi
  fi
  [ "$dod_trust_sep" = "true" ] || dod_trusted="false"
fi

if [ "$dod_trusted" != "true" ]; then
  # Hash the cmd so the confirm token is per-cmd-value (a swapped cmd re-prompts).
  # `sha256sum` is GNU-only and ABSENT on stock macOS — falling straight to the
  # literal "nohash" made EVERY cmd value share the `confirmed-nohash` token, so one
  # confirmation silently authorized any later (incl. maliciously swapped) command.
  # Fall back sha256sum -> shasum -a 256 (stock macOS) -> cksum (POSIX, universal);
  # tr keeps only hex/digit chars so the field survives each tool's output shape, and
  # cut -c1-16 keeps the Linux sha256sum token byte-identical (existing confirms hold).
  cmd_hash="$(printf '%s' "$dod_cmd" \
    | { sha256sum 2>/dev/null || shasum -a 256 2>/dev/null || cksum 2>/dev/null; } \
    | tr -dc '0-9a-f' | cut -c1-16)"
  [ -z "$cmd_hash" ] && cmd_hash="nohash"
  confirm_dir="${cwd}/.ravenclaude/runs/dod-gate/${safe_sid}"
  confirm_file="${confirm_dir}/confirmed-${cmd_hash}"
  if [ ! -f "$confirm_file" ]; then
    mkdir -p "$confirm_dir" 2>/dev/null || true
    _dod_bump_block
    if [ "$blocks" -ge "$max_blocks" ]; then
      _emit_hook_event "dod-gate.sh" "allow" "Stop" "$cmd_hash" "dod-first-run-untrusted-cap" 0
      _dod_force_stop "the command was not authorized, so it was not run"
    fi
    reason="$(_dod_not_done \
      "definition_of_done.cmd is not authorized for this session (attempt ${blocks}/${max_blocks}). This is not a test failure." \
      "A person approves this. Do not create the confirm file yourself. Creating it from this session is denied.
A person creates this file outside the agent:
  $confirm_file
The gate will then run:
  $dod_cmd
Do not redo the task. Do not ask the user whether you are done.
To trust this command for the repo, set definition_of_done.trusted: true in a later commit than the cmd line.
If you did not set this cmd, remove it from .ravenclaude/comfort-posture.yaml before doing anything else.
This refusal counts toward max_blocks. At the cap the verdict is STOP and the turn ends.")"
    # stdout JSON, exit 0. Copilot shows "hook exited with code 2" and drops
    # stderr when the hook exits 2, so the authorize-file reason never arrived.
    # decision:block on stdout is what both the Copilot harness and Local Chat read.
    printf '%s\n' "$reason" >&2
    if command -v jq >/dev/null 2>&1; then
      jq -cn --arg r "$reason" \
        '{decision:"block",reason:$r,hookSpecificOutput:{hookEventName:"Stop",decision:"block",reason:$r}}'
    fi
    _emit_hook_event "dod-gate.sh" "deny" "Stop" "$cmd_hash" "dod-first-run-untrusted" 0
    exit 0
  fi
fi

# Run the definition-of-done command — BOUNDED.
#
# `$dod_cmd` is an arbitrary user-configured shell command, run on every Stop.
# Unbounded, a command that hangs (a test suite waiting on a port, a linter on a
# pathological input, anything touching the network) wedges the session with no
# way out except the max_blocks counter — which never advances, because the
# command never returns. A gate that can hang is worse than no gate: it blocks
# work it was never meant to judge.
#
# _rc_timeout is the repo's portable shim (GNU timeout -> gtimeout -> perl),
# added for stock macOS where `timeout` does not exist. Sourced fail-safe: if the
# helper is missing the command still runs, unbounded, exactly as before — a
# missing helper must not disable the gate.
_dod_portable="$(dirname "${BASH_SOURCE[0]:-$0}")/_portable.sh"
[ -f "$_dod_portable" ] && . "$_dod_portable" 2>/dev/null || true
command -v _rc_timeout >/dev/null 2>&1 || _rc_timeout() { shift; "$@"; }

# 600s: long enough for a real test suite, short enough that a hang is survivable.
out="$(cd "$cwd" && _rc_timeout 600 bash -c "$dod_cmd" 2>&1)"; rc=$?
if [ "$rc" -eq 124 ] || [ "$rc" -eq 142 ]; then
  # GNU timeout reports 124; the perl fallback surfaces 142 (128+SIGALRM).
  out="$out
[dod-gate] the definition-of-done command exceeded 600s and was stopped."
fi

if [ "$rc" -eq 0 ]; then
  rm -f "$bf" 2>/dev/null || true
  exit 0   # no verdict line: DONE. The agent stops. Do not re-ask.
fi

_dod_bump_block

if [ "$blocks" -ge "$max_blocks" ]; then
  _dod_force_stop "the gate command has not exited 0"
fi

# Block the stop and feed the failing output back so the agent keeps working.
tail="$(printf '%s' "$out" | tail -c 1500 | tr -d '\000-\010\013\014\016-\037')"
reason="$(_dod_not_done \
  "gate command exit ${rc} (attempt ${blocks}/${max_blocks}): ${dod_cmd}" \
  "Failed output (tail):
${tail}")"
if command -v jq >/dev/null 2>&1; then
  # Top-level decision/reason is the Copilot harness contract (reason becomes
  # the next prompt). hookSpecificOutput is what Local VS Code Chat reads
  # (hooks-reference Stop output, fetched 2026-11-05). One object, both.
  jq -cn --arg r "$reason" \
    '{decision:"block",reason:$r,hookSpecificOutput:{hookEventName:"Stop",decision:"block",reason:$r}}'
else
  printf '%s\n' "$reason" >&2
  exit 2
fi
exit 0
