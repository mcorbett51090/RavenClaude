#!/usr/bin/env bash
# caveman-route-hook.sh — P3 of the caveman auto-routing plan
# (.ravenclaude/runs/forge/caveman-routing-decision-tree/plan.md § "P3 — Hook
# body, wired in SHADOW").
#
# The hook body wired into UserPromptSubmit + SessionStart(startup|resume|
# clear|fork), registered via the C2-(b) escape — `bash
# ${CLAUDE_PLUGIN_ROOT}/scripts/caveman-route-hook.sh --event {prompt|session}`
# — matching `ask-on-ambiguity.sh`'s own registration exactly. NOT in `hooks/`
# (C1: a new `hooks/*.sh` needs a chmod this substrate denies).
#
# ── SHADOW ONLY, this phase ─────────────────────────────────────────────────
# `shadow` is what "enabled" means for P3: decide, record, NEVER call the
# applier (`caveman-apply-mode.sh`). `live` mode's actual apply-call wiring is
# NOT built until a later phase (P7) — see the commented-out placeholder in
# `caveman-route-engine.py`. This script never invokes the applier, directly
# or indirectly, in this phase, regardless of which of shadow/live the posture
# names (both pass the short-circuit below and both decide+record only).
#
# ── The O(1) floor for non-adopters (first two lines of real logic) ────────
# `[ -f "$posture" ] || exit 0`, then ONE anchored grep for
# `caveman_routing: shadow|live`. Absent or `off` → exit 0, ZERO file writes
# of any kind — no state file, no route log, nothing. This mirrors
# `stream-prompt-attribute.sh`'s and `route-decision-review.sh`'s own
# zero-cost floor (C12: latency, not tokens, is this hook's real cost).
#
# ── Fail-open, unconditionally ──────────────────────────────────────────────
# Every path exits 0. The EXIT trap is armed FIRST (before anything can
# abort), and `-e` is deliberately absent so a failed command cannot become a
# non-zero exit — this hook must never be able to block or alter a prompt.
#
# ── Latency budget ───────────────────────────────────────────────────────────
# `RC_CAVEMAN_ROUTE_BUDGET_S` (default 3s, `[unverified]` per the plan) is
# enforced via `_rc_timeout` from `hooks/_portable.sh` (stock macOS has no GNU
# `timeout` — macOS door 2). The actual elapsed time is recorded by the
# engine in the route-log entry, so the guess is eventually replaced by a
# measurement (P5/P7's job to read that number back).
#
# bash 3.2-safe (C10): no `declare -A`, `mapfile`, `${x^^}`, `shopt -s
# globstar`. No GNU `timeout` / `grep -P` / `sed -i`.
trap 'exit 0' EXIT
set -uo pipefail

_run_hook() {
  # $1 = event ("prompt" | "session"), stdin = the hook payload.
  local event="$1"
  local project_dir="${CLAUDE_PROJECT_DIR:-}"
  [ -n "$project_dir" ] || return 0

  local posture="$project_dir/.ravenclaude/comfort-posture.yaml"
  [ -f "$posture" ] || return 0

  # ---- THE O(1) FLOOR: one anchored grep, absent/off -> exit 0, zero writes -
  grep -Eq '^[[:space:]]*caveman_routing:[[:space:]]*(shadow|live)[[:space:]]*$' \
    "$posture" 2>/dev/null || return 0

  local script_dir plugin_root hooks_dir engine budget
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)" || return 0
  plugin_root="$(cd "$script_dir/.." 2>/dev/null && pwd)" || return 0
  hooks_dir="$plugin_root/hooks"
  engine="$script_dir/caveman-route-engine.py"

  [ -f "$engine" ] || return 0
  command -v python3 >/dev/null 2>&1 || return 0

  # shellcheck source=/dev/null
  if [ -f "$hooks_dir/_portable.sh" ]; then
    . "$hooks_dir/_portable.sh" 2>/dev/null || true
  fi

  # P5 observability: source the shared emit helper so a real transition can
  # be recorded in hook-events.jsonl. Fail-safe stub mirrors
  # agent-dispatch-evaluator.sh's own pattern exactly — an absent helper
  # never blocks or alters anything, it just means no event gets written.
  # shellcheck source=/dev/null
  if [ -f "$hooks_dir/_emit-event.sh" ]; then
    . "$hooks_dir/_emit-event.sh" 2>/dev/null || true
  fi
  command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

  budget="${RC_CAVEMAN_ROUTE_BUDGET_S:-3}"

  # The hook payload is read ONCE into a local `payload` variable (the same
  # variable name _emit_hook_event's sourced session-resolution helper
  # expects to find in the caller's scope, per _emit-event.sh's own
  # documented resolution order) and then fed to the engine verbatim over a
  # pipe — never re-serialized or mutated, so nothing in this bash layer can
  # mangle it. stdout is captured (was previously discarded) so a single
  # `SIGNAL <token>` line — the engine's ONLY possible stdout output, see
  # caveman-route-engine.py's own "P5 observability" section — can be turned
  # into exactly one _emit_hook_event call.
  local payload out
  payload="$(cat 2>/dev/null || true)"

  if command -v _rc_timeout >/dev/null 2>&1; then
    out="$(printf '%s' "$payload" \
      | _rc_timeout "$budget" python3 "$engine" --event "$event" 2>/dev/null)" || true
  else
    out="$(printf '%s' "$payload" | python3 "$engine" --event "$event" 2>/dev/null)" || true
  fi

  # ---- P5 observability emit: EXACTLY the plan's literal call shape -------
  # `_emit_hook_event "caveman-route-hook.sh" "warn" "" "" "<verdict-token>" 0`
  # on a transition, never on hold. `path` is deliberately EMPTY (the
  # substrate carries a derived enum token, never a prompt/command/path —
  # C8), matching agent-dispatch-evaluator.sh's own serial-dispatch signal.
  case "${out:-}" in
    SIGNAL\ caveman-route-*)
      _emit_hook_event "caveman-route-hook.sh" "warn" "" "" \
        "${out#SIGNAL }" 0 2>/dev/null || true
      ;;
  esac
  return 0
}

# =============================================================================
# --self-test
# =============================================================================
# Every fixture below is isolated: a fresh temp dir stands in for
# CLAUDE_PROJECT_DIR (and, for the must-fail half only, CLAUDE_CONFIG_DIR),
# so nothing ever touches real host state. Positive controls follow this
# repo's own probe-discipline convention (a probe that always reads clean is
# worthless).

_ST_FAIL=0
_ST_TOTAL=0
_ST_PASS=0
_ok()   { printf '  OK   %s\n' "$1"; _ST_TOTAL=$((_ST_TOTAL + 1)); _ST_PASS=$((_ST_PASS + 1)); }
_fail() { printf '  FAIL %s\n' "$1"; _ST_FAIL=1; _ST_TOTAL=$((_ST_TOTAL + 1)); }

_st_write_posture() {
  # $1 = dest dir (project root)  $2 = caveman_routing value (or "" for absent)
  mkdir -p "$1/.ravenclaude"
  if [ -n "$2" ]; then
    printf 'caveman_routing: %s\n' "$2" > "$1/.ravenclaude/comfort-posture.yaml"
  fi
}

_st_write_transcript() {
  # $1 = dest path. A minimal, valid JSONL transcript: a few assistant
  # responses with prose text (a "clean" shape the classifier can read
  # without incident — the exact verdict doesn't matter for these tests,
  # only that a decision gets made and logged).
  local i
  : > "$1"
  for i in 1 2 3; do
    printf '{"type":"assistant","requestId":"req_%d","message":{"id":"msg_%d","content":[{"type":"text","text":"a clean prose turn."}],"usage":{"output_tokens":10}}}\n' \
      "$i" "$i" >> "$1"
  done
}

_st_write_malformed_transcript() {
  # $1 = dest path. Not valid JSONL at all.
  printf 'this is not json at all {{{\nneither is this\n' > "$1"
}

_st_write_clean_streak_transcript() {
  # $1 = dest path. FIVE clean prose-only assistant responses (no tool_use,
  # nonzero text) — one more than DEFAULT_ENABLE_STREAK (4), so a PRESERVED
  # cursor (which reads the whole file) computes a real "on"/"on:clean-streak"
  # verdict, while a RESET cursor (cursor_byte=None) forces "off:bootstrap"
  # regardless of this same content — the P4 reset-vs-preserve fixtures'
  # single distinguishing signal (see caveman-route.py's own
  # classify_window()/bootstrap-force logic).
  local i
  : > "$1"
  for i in 1 2 3 4 5; do
    printf '{"type":"assistant","requestId":"creq_%d","message":{"id":"cmsg_%d","content":[{"type":"text","text":"a clean prose turn."}],"usage":{"output_tokens":10}}}\n' \
      "$i" "$i" >> "$1"
  done
}

_st_write_router_state() {
  # $1 = dest project dir  $2 = session id  $3 = cursor_byte (int)
  # Seeds the router's OWN state file directly — an explicit, non-null
  # cursor_byte (0) so a PRESERVING call reads a real int (bootstrap=False)
  # while a RESETTING call still forces cursor_byte=None regardless of what
  # is written here. streak/verdict are deliberately implausible sentinels
  # (99 / "on") so a bug that failed to override them on reset would be
  # visible in the post-call state, not just inferred from the verdict.
  local dir="$1/.ravenclaude/runs/$2"
  mkdir -p "$dir"
  printf '{"cursor_byte": %d, "streak": 99, "verdict": "on"}\n' "$3" \
    > "$dir/caveman-route-state.json"
}

_st_good_caveman_fixture() {
  # $1 = destination .js path. Same faithful re-implementation
  # caveman-apply-mode.sh's own self-test uses (verbatim writeSessionMode
  # body from plan.md).
  cat > "$1" <<'RC_GOOD_FIXTURE'
'use strict';
const fs = require('fs');
const path = require('path');
const VALID_MODES = ['off', 'lite', 'full'];
function sessionActivePath(claudeDir, sessionId) {
  if (!/^[A-Za-z0-9_-]{1,128}$/.test(sessionId)) return null;
  return path.join(claudeDir, '.caveman-sessions', sessionId + '.mode');
}
function legacyFlagPath(claudeDir) { return path.join(claudeDir, '.caveman-active'); }
function safeWriteFlag(p, val) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  const tmp = p + '.tmp-' + process.pid;
  fs.writeFileSync(tmp, val, { mode: 0o600 });
  fs.renameSync(tmp, p);
}
function readFlag(p) { try { return fs.readFileSync(p, 'utf8').trim(); } catch (e) { return null; } }
function offToNull(v) { return (!v || v === 'off') ? null : v; }
function writeSessionMode(claudeDir, sessionId, modeOrNull) {
  const canonical = (!modeOrNull || modeOrNull === 'off') ? 'off' : modeOrNull;
  if (!VALID_MODES.includes(canonical)) return;
  const sessionPath = sessionActivePath(claudeDir, sessionId);
  if (sessionPath) safeWriteFlag(sessionPath, canonical);
  const legacy = legacyFlagPath(claudeDir);
  if (canonical === 'off') { try { fs.unlinkSync(legacy); } catch (e) {} }
  else { safeWriteFlag(legacy, canonical); }
}
function readSessionModeRaw(claudeDir, sessionId) {
  const p = sessionActivePath(claudeDir, sessionId);
  if (!p) return null;
  return readFlag(p);
}
function resolveActiveMode(claudeDir, sessionId) {
  const sessionPath = sessionActivePath(claudeDir, sessionId);
  if (sessionPath) {
    const stored = readFlag(sessionPath);
    if (stored !== null) return offToNull(stored);
  }
  return offToNull(readFlag(legacyFlagPath(claudeDir)));
}
function getDefaultMode() { return 'off'; }
module.exports = { writeSessionMode, readSessionModeRaw, resolveActiveMode, getDefaultMode, VALID_MODES };
RC_GOOD_FIXTURE
}

cmd_self_test() {
  # NOTE: st_root is intentionally NOT `local` — see caveman-apply-mode.sh's
  # own self-test for why (the EXIT trap must see it after this function's
  # scope tears down).
  st_root="$(mktemp -d "${TMPDIR:-/tmp}/rc-caveman-route-hook-st.XXXXXX")"
  trap 'rm -rf "${st_root:-}"' EXIT
  local script_self plugin_root
  script_self="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)/$(basename "${BASH_SOURCE[0]:-$0}")"
  plugin_root="$(cd "$(dirname "$script_self")/.." && pwd)"

  # ---- Test 1: absent posture -> exit 0, state file NOT created (asserted
  # positively) --------------------------------------------------------------
  local t1_proj t1_sid t1_transcript rc1
  t1_proj="$st_root/t1/project"
  mkdir -p "$t1_proj"
  t1_sid="t1-session"
  t1_transcript="$t1_proj/transcript.jsonl"
  _st_write_transcript "$t1_transcript"
  rc1=0
  CLAUDE_PROJECT_DIR="$t1_proj" bash "$script_self" --event prompt \
    <<< "{\"session_id\":\"$t1_sid\",\"transcript_path\":\"$t1_transcript\"}" \
    >/dev/null 2>&1 || rc1=$?
  if [ "$rc1" -eq 0 ] && [ ! -e "$t1_proj/.ravenclaude/runs/$t1_sid/caveman-route-state.json" ] \
     && [ ! -e "$t1_proj/.ravenclaude/runs/$t1_sid/caveman-route.jsonl" ]; then
    _ok "absent-posture: exit 0, state file NOT created, route log NOT created (asserted positively)"
  else
    _fail "absent-posture: expected exit 0 and no writes, got rc=$rc1 state-exists=$([ -e "$t1_proj/.ravenclaude/runs/$t1_sid/caveman-route-state.json" ] && echo yes || echo no)"
  fi

  # ---- Test 2: caveman_routing: off -> same as test 1 -----------------------
  local t2_proj t2_sid t2_transcript rc2
  t2_proj="$st_root/t2/project"
  mkdir -p "$t2_proj"
  t2_sid="t2-session"
  t2_transcript="$t2_proj/transcript.jsonl"
  _st_write_transcript "$t2_transcript"
  _st_write_posture "$t2_proj" "off"
  rc2=0
  CLAUDE_PROJECT_DIR="$t2_proj" bash "$script_self" --event prompt \
    <<< "{\"session_id\":\"$t2_sid\",\"transcript_path\":\"$t2_transcript\"}" \
    >/dev/null 2>&1 || rc2=$?
  if [ "$rc2" -eq 0 ] && [ ! -e "$t2_proj/.ravenclaude/runs/$t2_sid/caveman-route-state.json" ] \
     && [ ! -e "$t2_proj/.ravenclaude/runs/$t2_sid/caveman-route.jsonl" ]; then
    _ok "caveman_routing=off: exit 0, no writes (asserted positively)"
  else
    _fail "caveman_routing=off: expected exit 0 and no writes, got rc=$rc2"
  fi

  # ---- Test 3: caveman_routing: shadow -> a decision line lands in the route
  # log AND the caveman session mode file is byte-identical before/after.
  # This is the POSITIVE CONTROL for tests 1/2 (proves the harness CAN write
  # when configured to) and doubles as the "shadow never mutates the mode
  # file" acceptance test. -----------------------------------------------
  local t3_proj t3_cfg t3_sid t3_transcript t3_mode_file rc3 before3 after3
  t3_proj="$st_root/t3/project"
  t3_cfg="$st_root/t3/claude-config"
  mkdir -p "$t3_proj" "$t3_cfg/.caveman-sessions"
  t3_sid="t3-session"
  t3_transcript="$t3_proj/transcript.jsonl"
  _st_write_transcript "$t3_transcript"
  _st_write_posture "$t3_proj" "shadow"
  t3_mode_file="$t3_cfg/.caveman-sessions/$t3_sid.mode"
  printf 'PRESEED-UNTOUCHED' > "$t3_mode_file"
  before3="$(cat "$t3_mode_file")"
  rc3=0
  CLAUDE_PROJECT_DIR="$t3_proj" CLAUDE_CONFIG_DIR="$t3_cfg" \
    bash "$script_self" --event prompt \
    <<< "{\"session_id\":\"$t3_sid\",\"transcript_path\":\"$t3_transcript\"}" \
    >/dev/null 2>&1 || rc3=$?
  after3="$(cat "$t3_mode_file")"
  if [ "$rc3" -eq 0 ] \
     && [ -f "$t3_proj/.ravenclaude/runs/$t3_sid/caveman-route.jsonl" ] \
     && [ "$(wc -l < "$t3_proj/.ravenclaude/runs/$t3_sid/caveman-route.jsonl" | tr -d '[:space:]')" -ge 1 ] \
     && [ "$before3" = "$after3" ]; then
    _ok "shadow: decision line in route log, mode file byte-identical before/after (before='$before3' after='$after3')"
  else
    _fail "shadow: expected route-log line + byte-identical mode file, got rc=$rc3 before='$before3' after='$after3' log-exists=$([ -f "$t3_proj/.ravenclaude/runs/$t3_sid/caveman-route.jsonl" ] && echo yes || echo no)"
  fi

  # ---- Test 4 (must-fail half): with the shadow gate REMOVED (a scratch
  # mutant that uncomments the P7 placeholder in caveman-route-engine.py),
  # the SAME request against the SAME caveman fixture DOES change the mode
  # file. Then confirm the REAL script, run again with a fresh session id
  # against the identical config, does NOT. --------------------------------
  local t4_root t4_proj t4_cfg t4_sid mutant_dir mutant_engine mutant_apply \
        t4_transcript t4_mode_file mid4 final4 rc4a rc4b
  t4_root="$st_root/t4"
  t4_proj="$t4_root/project"
  t4_cfg="$t4_root/claude-config"
  mutant_dir="$t4_root/mutant-scripts"
  mkdir -p "$t4_proj" "$t4_cfg/.caveman-sessions" "$mutant_dir"
  t4_sid="t4-session"
  t4_transcript="$t4_proj/transcript.jsonl"
  _st_write_transcript "$t4_transcript"
  _st_write_posture "$t4_proj" "live"

  # Build the mutant: strip the "# CAVEMAN_P7:" prefix, uncommenting the
  # placeholder's applier call. sed -E is POSIX/BSD-portable (no -i, no -P).
  mutant_engine="$mutant_dir/caveman-route-engine.py"
  sed -E 's/^([[:space:]]*)# CAVEMAN_P7:(.*)$/\1\2/' \
    "$plugin_root/scripts/caveman-route-engine.py" > "$mutant_engine"
  mutant_apply="$mutant_dir/caveman-apply-mode.sh"
  cp "$plugin_root/scripts/caveman-apply-mode.sh" "$mutant_apply"
  # The mutant engine also resolves caveman-route.py as its OWN sibling (by
  # file path, from its own __file__), so the classifier must be copied
  # alongside it too, or _load_classifier() throws and the mutant fails open
  # for an unrelated reason (a missing file, not the gate under test).
  cp "$plugin_root/scripts/caveman-route.py" "$mutant_dir/caveman-route.py"

  t4_mode_file="$t4_cfg/.caveman-sessions/$t4_sid.mode"

  # 4a: real caveman fixture present -> the MUTANT engine, invoked directly
  # (same env a hook call would use), should change the mode file.
  local t4_cache_hash_dir
  t4_cache_hash_dir="$t4_cfg/plugins/cache/caveman/caveman/abc123def456/src/hooks"
  mkdir -p "$t4_cache_hash_dir"
  _st_good_caveman_fixture "$t4_cache_hash_dir/caveman-config.js"

  rc4a=0
  CLAUDE_PROJECT_DIR="$t4_proj" CLAUDE_CONFIG_DIR="$t4_cfg" \
    python3 "$mutant_engine" --event prompt \
    <<< "{\"session_id\":\"$t4_sid\",\"transcript_path\":\"$t4_transcript\"}" \
    >/dev/null 2>&1 || rc4a=$?
  mid4="$(cat "$t4_mode_file" 2>/dev/null || echo '<absent>')"

  if [ "$mid4" != "<absent>" ]; then
    _ok "must-fail-half (mutant): shadow gate removed -> mode file WAS created/changed (now '$mid4') — proves the gate is load-bearing"
  else
    _fail "must-fail-half (mutant): expected the mode file to change with the gate removed, but it stayed absent (rc=$rc4a) — the teeth test itself is broken"
  fi

  # 4b: the REAL script, same config/fixture, a fresh session id -> mode
  # file for THIS session must never be created at all.
  local t4b_sid t4b_mode_file rc4b_local
  t4b_sid="t4b-session"
  t4b_mode_file="$t4_cfg/.caveman-sessions/$t4b_sid.mode"
  rc4b_local=0
  CLAUDE_PROJECT_DIR="$t4_proj" CLAUDE_CONFIG_DIR="$t4_cfg" \
    bash "$script_self" --event prompt \
    <<< "{\"session_id\":\"$t4b_sid\",\"transcript_path\":\"$t4_transcript\"}" \
    >/dev/null 2>&1 || rc4b_local=$?
  final4="$(cat "$t4b_mode_file" 2>/dev/null || echo '<absent>')"
  if [ "$rc4b_local" -eq 0 ] && [ "$final4" = "<absent>" ]; then
    _ok "shadow gate (real script): identical config/fixture, real script -> mode file stays absent (control: 4a proves the gate is what prevents this)"
  else
    _fail "shadow gate (real script): expected mode file to stay absent, got '$final4' (rc=$rc4b_local)"
  fi

  # ---- Test 5: malformed transcript -> exit 0, no state corruption. -------
  local t5_proj t5_sid t5_transcript rc5 state5_valid
  t5_proj="$st_root/t5/project"
  mkdir -p "$t5_proj"
  t5_sid="t5-session"
  t5_transcript="$t5_proj/transcript.jsonl"
  _st_write_malformed_transcript "$t5_transcript"
  _st_write_posture "$t5_proj" "shadow"
  rc5=0
  CLAUDE_PROJECT_DIR="$t5_proj" bash "$script_self" --event prompt \
    <<< "{\"session_id\":\"$t5_sid\",\"transcript_path\":\"$t5_transcript\"}" \
    >/dev/null 2>&1 || rc5=$?
  state5_valid="yes"
  if [ -f "$t5_proj/.ravenclaude/runs/$t5_sid/caveman-route-state.json" ]; then
    python3 -c "import json,sys; json.load(open(sys.argv[1]))" \
      "$t5_proj/.ravenclaude/runs/$t5_sid/caveman-route-state.json" >/dev/null 2>&1 || state5_valid="no"
  fi
  if [ "$rc5" -eq 0 ] && [ "$state5_valid" = "yes" ]; then
    _ok "malformed-transcript: exit 0, no state corruption (state file, if any, is valid JSON)"
  else
    _fail "malformed-transcript: expected exit 0 and valid/absent state, got rc=$rc5 state-valid=$state5_valid"
  fi

  # ===========================================================================
  # P4 (plan.md "SessionStart re-arm and the reset race") — source-branching
  # fixtures. Every case below seeds the SAME router state (an explicit,
  # non-null cursor_byte=0, plus implausible sentinel streak/verdict values
  # that would never occur naturally — see _st_write_router_state) against
  # the SAME 5-clean-response transcript, then fires ONLY `source` differently
  # and checks the resulting verdict/why: a RESET source must force
  # "off"/"off:bootstrap" (caveman's own re-derived default is the safe
  # direction); a PRESERVING source must show the real, continued
  # "on"/"on:clean-streak" result. This is the single distinguishing signal
  # (see caveman-route.py's own bootstrap-forces-off logic) — deliberately
  # NOT a diff on cursor_byte, which coincides at 0 for both paths on a small
  # transcript and would not discriminate.
  # ===========================================================================

  _st_source_case() {
    # $1=source value  $2=expected verdict  $3=expected why  $4=expected
    # reset ("true"|"false")  $5=fixture label
    local src="$1" exp_verdict="$2" exp_why="$3" exp_reset="$4" label="$5"
    local proj sid transcript rc state_path log_path result
    proj="$st_root/src-${label}/project"
    mkdir -p "$proj"
    sid="src-${label}-session"
    transcript="$proj/transcript.jsonl"
    _st_write_clean_streak_transcript "$transcript"
    _st_write_posture "$proj" "shadow"
    _st_write_router_state "$proj" "$sid" 0
    state_path="$proj/.ravenclaude/runs/$sid/caveman-route-state.json"
    log_path="$proj/.ravenclaude/runs/$sid/caveman-route.jsonl"
    rc=0
    CLAUDE_PROJECT_DIR="$proj" bash "$script_self" --event session \
      <<< "{\"session_id\":\"$sid\",\"transcript_path\":\"$transcript\",\"source\":\"$src\"}" \
      >/dev/null 2>&1 || rc=$?
    result="$(python3 -c "
import json, sys
state_p, log_p = sys.argv[1], sys.argv[2]
try:
    state = json.load(open(state_p))
except Exception:
    state = {}
try:
    lines = [l for l in open(log_p).read().splitlines() if l.strip()]
    last = json.loads(lines[-1]) if lines else {}
except Exception:
    last = {}
print(state.get('verdict'))
print(last.get('why'))
print('true' if last.get('reset') else 'false')
print(last.get('source'))
" "$state_path" "$log_path" 2>/dev/null)"
    local got_verdict got_why got_reset got_source
    got_verdict="$(printf '%s\n' "$result" | sed -n '1p')"
    got_why="$(printf '%s\n' "$result" | sed -n '2p')"
    got_reset="$(printf '%s\n' "$result" | sed -n '3p')"
    got_source="$(printf '%s\n' "$result" | sed -n '4p')"
    if [ "$rc" -eq 0 ] && [ "$got_verdict" = "$exp_verdict" ] && [ "$got_why" = "$exp_why" ] \
       && [ "$got_reset" = "$exp_reset" ]; then
      _ok "source=$src ($label): verdict=$got_verdict why=$got_why reset=$got_reset source-logged=$got_source"
    else
      _fail "source=$src ($label): expected verdict=$exp_verdict why=$exp_why reset=$exp_reset, got rc=$rc verdict=$got_verdict why=$got_why reset=$got_reset source-logged=$got_source"
    fi
  }

  # ---- Test 6/7: startup|clear -> state RESET (verdict forced "off", the
  # safe direction) regardless of the seeded prior state's sentinel values. -
  _st_source_case "startup" "off" "off:bootstrap"   "true"  "startup"
  _st_source_case "clear"   "off" "off:bootstrap"   "true"  "clear"

  # ---- Test 8/9: resume|fork -> state PRESERVED (the real "on" verdict the
  # window computes, using the seeded cursor rather than a forced bootstrap). -
  _st_source_case "resume"  "on"  "on:clean-streak" "false" "resume"
  _st_source_case "fork"    "on"  "on:clean-streak" "false" "fork"

  # ---- Test 10: a FABRICATED source "compact" -> does NOT reset (this hook
  # has no `compact` matcher registered at all -- see hooks.json's comment on
  # this entry -- so this can only arrive as a fabricated/defense-in-depth
  # payload; it must still PRESERVE, matching resume/fork, never accidentally
  # reset on an unrecognized-but-real Claude Code source value). -------------
  _st_source_case "compact" "on"  "on:clean-streak" "false" "compact-fabricated"

  # ---- Test 11 (must-fail half): source-branching REMOVED -- a mutant that
  # forces `is_reset = True` unconditionally (every SessionStart source,
  # including resume/fork, treated as a RESET) must show resume LOSING its
  # earned streak (verdict flips "on" -> "off"), proving the branching this
  # phase added is load-bearing, not decorative. Control (11b): the REAL
  # script, run against the IDENTICAL config/transcript with a fresh session
  # id, still correctly preserves. ------------------------------------------
  local t11_root t11_proj mutant11_dir mutant11_engine t11_transcript t11_sid \
        t11_real_sid rc11a rc11b mutant11_verdict real11_verdict
  t11_root="$st_root/t11"
  t11_proj="$t11_root/project"
  mutant11_dir="$t11_root/mutant-scripts"
  mkdir -p "$t11_proj" "$mutant11_dir"
  t11_transcript="$t11_proj/transcript.jsonl"
  _st_write_clean_streak_transcript "$t11_transcript"
  _st_write_posture "$t11_proj" "shadow"

  # Build the mutant: strip the source-branching decision, forcing
  # is_reset=True on every call regardless of `source`. sed -E is
  # POSIX/BSD-portable (no -i, no -P), matching P3's own mutant technique.
  mutant11_engine="$mutant11_dir/caveman-route-engine.py"
  sed -E 's/^([[:space:]]*)is_reset = isinstance\(raw_source, str\) and raw_source in _RESET_SOURCES$/\1is_reset = True  # MUTANT: always reset, ignoring source/' \
    "$plugin_root/scripts/caveman-route-engine.py" > "$mutant11_engine"
  # The mutant also resolves caveman-route.py as its OWN sibling (by file
  # path, from its own __file__), so the classifier must be copied alongside
  # it too -- matching P3 test4's own established pattern.
  cp "$plugin_root/scripts/caveman-route.py" "$mutant11_dir/caveman-route.py"

  # 11a: mutant, source=resume (should PRESERVE, real script shows "on") ->
  # with the branching stripped, it incorrectly RESETS -> "off".
  t11_sid="t11-mutant-session"
  _st_write_router_state "$t11_proj" "$t11_sid" 0
  rc11a=0
  CLAUDE_PROJECT_DIR="$t11_proj" python3 "$mutant11_engine" --event session \
    <<< "{\"session_id\":\"$t11_sid\",\"transcript_path\":\"$t11_transcript\",\"source\":\"resume\"}" \
    >/dev/null 2>&1 || rc11a=$?
  mutant11_verdict="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('verdict'))" \
    "$t11_proj/.ravenclaude/runs/$t11_sid/caveman-route-state.json" 2>/dev/null)"
  if [ "$mutant11_verdict" = "off" ]; then
    _ok "must-fail-half (mutant): source-branching stripped -> resume incorrectly RESETS (verdict flips 'on' -> 'off'), losing its streak -- proves the branching is load-bearing"
  else
    _fail "must-fail-half (mutant): expected the stripped-branching mutant to lose resume's streak (verdict 'off'), got '$mutant11_verdict' (rc=$rc11a) -- the teeth test itself is broken"
  fi

  # 11b: the REAL script, identical config/transcript, a fresh session id ->
  # resume still correctly PRESERVES (verdict stays "on").
  t11_real_sid="t11-real-session"
  _st_write_router_state "$t11_proj" "$t11_real_sid" 0
  rc11b=0
  CLAUDE_PROJECT_DIR="$t11_proj" bash "$script_self" --event session \
    <<< "{\"session_id\":\"$t11_real_sid\",\"transcript_path\":\"$t11_transcript\",\"source\":\"resume\"}" \
    >/dev/null 2>&1 || rc11b=$?
  real11_verdict="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('verdict'))" \
    "$t11_proj/.ravenclaude/runs/$t11_real_sid/caveman-route-state.json" 2>/dev/null)"
  if [ "$rc11b" -eq 0 ] && [ "$real11_verdict" = "on" ]; then
    _ok "source-branching (real script): identical config/transcript, real script -> resume correctly PRESERVES (verdict stays 'on') (control: 11a proves the branching is what prevents the loss)"
  else
    _fail "source-branching (real script): expected resume to preserve (verdict 'on'), got '$real11_verdict' (rc=$rc11b)"
  fi

  # ===========================================================================
  # P5 (plan.md "Observability + offline replay calibration") — transition-
  # only emission fixtures. Acceptance test (a) (>=1 JSONL line in shadow
  # mode) is already re-confirmed by test 3 above; these cover the NEW P5
  # invariants: emit on a real transition, NEVER on hold/a repeat, with a
  # must-fail half proving the gate (not an artifact of the fixtures) is
  # what limits emission count.
  # ===========================================================================

  _st_append_four_clean_responses() {
    # $1 = existing transcript path, APPENDED to (simulates live transcript
    # growth between calls — msg ids 4..7, distinct from the base fixture's
    # 1..3, so C6 dedupe sees them as new responses, not re-reads).
    local i
    for i in 4 5 6 7; do
      printf '{"type":"assistant","requestId":"areq_%d","message":{"id":"amsg_%d","content":[{"type":"text","text":"a clean prose turn appended."}],"usage":{"output_tokens":10}}}\n' \
        "$i" "$i" >> "$1"
    done
  }

  local t12_proj t12_sid t12_transcript t12_events rc12
  t12_proj="$st_root/t12/project"
  mkdir -p "$t12_proj"
  t12_sid="t12-session"
  t12_transcript="$t12_proj/transcript.jsonl"
  _st_write_transcript "$t12_transcript"
  _st_write_posture "$t12_proj" "shadow"
  t12_events="$t12_proj/.ravenclaude/runs/$t12_sid/hook-events.jsonl"

  # ---- Test 12: session's FIRST call (bootstrap forces "off") is a real
  # transition (None -> "off") -> exactly one warn event, the plan's own
  # literal call shape (tool="" path="" rule=<token>). --------------------
  rc12=0
  CLAUDE_PROJECT_DIR="$t12_proj" bash "$script_self" --event prompt \
    <<< "{\"session_id\":\"$t12_sid\",\"transcript_path\":\"$t12_transcript\"}" \
    >/dev/null 2>&1 || rc12=$?
  if [ "$rc12" -eq 0 ] && [ -f "$t12_events" ] \
     && [ "$(wc -l < "$t12_events" | tr -d '[:space:]')" -eq 1 ]; then
    local ev12
    ev12="$(python3 -c "
import json
e = json.loads(open('$t12_events').read().splitlines()[0])
for k in ('hook', 'verdict', 'tool', 'path', 'rule', 'exit_code'):
    print(repr(e.get(k)))
" 2>/dev/null)"
    local exp12
    exp12="'caveman-route-hook.sh'
'warn'
''
''
'caveman-route-shadow-off'
0"
    if [ "$ev12" = "$exp12" ]; then
      _ok "observability: session's first call (bootstrap) emits exactly 1 warn event, the plan's literal shape (hook=caveman-route-hook.sh verdict=warn tool='' path='' rule=caveman-route-shadow-off exit_code=0)"
    else
      _fail "observability: expected the plan's literal shape, got:
$ev12"
    fi
  else
    _fail "observability: expected exactly 1 hook-events.jsonl line after the first call, events-file=$([ -f "$t12_events" ] && wc -l < "$t12_events" || echo absent)"
  fi

  # ---- Test 13: SAME session, second call, transcript UNCHANGED -> the
  # incremental cursor has already consumed it, so the window is empty and
  # the verdict is "hold" -> NO new event (event count stays 1). -----------
  local rc13
  rc13=0
  CLAUDE_PROJECT_DIR="$t12_proj" bash "$script_self" --event prompt \
    <<< "{\"session_id\":\"$t12_sid\",\"transcript_path\":\"$t12_transcript\"}" \
    >/dev/null 2>&1 || rc13=$?
  if [ "$rc13" -eq 0 ] && [ "$(wc -l < "$t12_events" | tr -d '[:space:]')" -eq 1 ]; then
    _ok "observability: repeat call with no verdict change (hold) -> NO new event (still 1 line, never on hold)"
  else
    _fail "observability: expected event count to stay at 1 on a hold/repeat call, got $(wc -l < "$t12_events" 2>/dev/null || echo absent)"
  fi

  # ---- Test 14: SAME session, transcript GROWS with 4 more clean prose
  # responses (a real "off" -> "on" transition) -> exactly ONE more event
  # (total 2), the second carrying caveman-route-shadow-on. -----------------
  local rc14 t14_count last14_rule
  _st_append_four_clean_responses "$t12_transcript"
  rc14=0
  CLAUDE_PROJECT_DIR="$t12_proj" bash "$script_self" --event prompt \
    <<< "{\"session_id\":\"$t12_sid\",\"transcript_path\":\"$t12_transcript\"}" \
    >/dev/null 2>&1 || rc14=$?
  t14_count="$(wc -l < "$t12_events" 2>/dev/null | tr -d '[:space:]')"
  last14_rule="$(python3 -c "
import json
lines = [l for l in open('$t12_events').read().splitlines() if l.strip()]
print(json.loads(lines[-1]).get('rule') if lines else '')
" 2>/dev/null)"
  if [ "$rc14" -eq 0 ] && [ "$t14_count" = "2" ] && [ "$last14_rule" = "caveman-route-shadow-on" ]; then
    _ok "observability: transcript grows into a real off->on transition -> exactly 1 new event (total 2), rule=caveman-route-shadow-on"
  else
    _fail "observability: expected 2 total events with the newest rule=caveman-route-shadow-on, got count=$t14_count last-rule=$last14_rule (rc=$rc14)"
  fi

  # ---- Test 15 (must-fail half): a mutant that emits on EVERY call
  # (strips the `if is_transition:` gate) shows MORE events than the real
  # script over the identical 2-call (transition, then hold) sequence --
  # proving the gate is load-bearing, not decorative. Control: the REAL
  # script, same config/transcript, fresh session id -> exactly 1 event. ---
  local t15_root t15_proj mutant15_dir mutant15_engine t15_transcript t15_sid \
        t15_real_sid rc15a rc15b mutant15_count real15_count
  t15_root="$st_root/t15"
  t15_proj="$t15_root/project"
  mutant15_dir="$t15_root/mutant-scripts"
  mkdir -p "$t15_proj" "$mutant15_dir"
  t15_transcript="$t15_proj/transcript.jsonl"
  _st_write_transcript "$t15_transcript"
  _st_write_posture "$t15_proj" "shadow"

  mutant15_engine="$mutant15_dir/caveman-route-engine.py"
  sed -E 's/^([[:space:]]*)if is_transition:$/\1if True:  # MUTANT: always emit, ignoring is_transition/' \
    "$plugin_root/scripts/caveman-route-engine.py" > "$mutant15_engine"
  cp "$plugin_root/scripts/caveman-route.py" "$mutant15_dir/caveman-route.py"

  t15_sid="t15-mutant-session"
  # NOTE: this drives the mutant ENGINE directly (as the hook wrapper would
  # invoke it), NOT through _emit_hook_event (the engine only prints SIGNAL
  # lines; the shell owns the emit) -- so the observable teeth signal here
  # is the mutant printing 2 SIGNAL lines total (one per call, the second
  # of which is a HOLD under the real gate) instead of 1.
  mutant15_count="$( { \
    CLAUDE_PROJECT_DIR="$t15_proj" python3 "$mutant15_engine" --event prompt \
      <<< "{\"session_id\":\"$t15_sid\",\"transcript_path\":\"$t15_transcript\"}"; \
    CLAUDE_PROJECT_DIR="$t15_proj" python3 "$mutant15_engine" --event prompt \
      <<< "{\"session_id\":\"$t15_sid\",\"transcript_path\":\"$t15_transcript\"}"; \
  } 2>/dev/null | grep -c '^SIGNAL ' || true)"
  rc15a=0
  if [ "$mutant15_count" -ge 2 ]; then
    _ok "must-fail-half (mutant): is_transition gate stripped -> emits on every call ($mutant15_count SIGNAL lines over 2 calls, one of which is a hold under the real gate) -- proves the gate is load-bearing"
  else
    _fail "must-fail-half (mutant): expected >=2 SIGNAL lines with the gate stripped, got $mutant15_count -- the teeth test itself is broken"
  fi

  t15_real_sid="t15-real-session"
  rc15b=0
  CLAUDE_PROJECT_DIR="$t15_proj" bash "$script_self" --event prompt \
    <<< "{\"session_id\":\"$t15_real_sid\",\"transcript_path\":\"$t15_transcript\"}" \
    >/dev/null 2>&1 || rc15b=$?
  CLAUDE_PROJECT_DIR="$t15_proj" bash "$script_self" --event prompt \
    <<< "{\"session_id\":\"$t15_real_sid\",\"transcript_path\":\"$t15_transcript\"}" \
    >/dev/null 2>&1 || rc15b=$?
  real15_count="$(wc -l < "$t15_proj/.ravenclaude/runs/$t15_real_sid/hook-events.jsonl" 2>/dev/null | tr -d '[:space:]')"
  if [ "$rc15b" -eq 0 ] && [ "$real15_count" = "1" ]; then
    _ok "observability gate (real script): identical config/transcript, 2 calls (transition then hold) -> exactly 1 event (control: 15's mutant proves the gate is what prevents the second)"
  else
    _fail "observability gate (real script): expected exactly 1 event over the 2-call sequence, got $real15_count (rc=$rc15b)"
  fi

  # ===========================================================================
  # P5 acceptance test (b) — NO-EGRESS. A sentinel planted in a synthetic
  # "prompt" (a user-type text block) AND a synthetic "tool result" (a
  # user-type tool_result block) must NEVER appear anywhere this hook
  # writes — the Gate 110/Gate 186 shape: a real assertion with a must-fail
  # half that PROVES a leak would be caught, not just an absence nobody
  # tested for.
  # ===========================================================================

  _st_write_sentinel_transcript() {
    # $1 = dest path  $2 = prompt sentinel  $3 = tool-result sentinel
    : > "$1"
    printf '{"type":"user","message":{"content":[{"type":"text","text":"%s"}]}}\n' "$2" >> "$1"
    printf '{"type":"user","message":{"content":[{"type":"tool_result","content":[{"type":"text","text":"%s"}]}]}}\n' "$3" >> "$1"
    # A few real assistant responses so the classifier has something to
    # decide over (type=="user" lines above are already excluded by
    # construction -- classify() only reads type=="assistant" -- this is
    # what the positive half of this test PROVES, end-to-end through this
    # hook's own file outputs, not just the classifier's isolated fixture).
    _st_write_transcript "$1.assistant_tmp"
    cat "$1.assistant_tmp" >> "$1"
    rm -f "$1.assistant_tmp"
  }

  local sentinel_prompt sentinel_toolresult t16_proj t16_sid t16_transcript rc16 \
        t16_run_dir leak16
  sentinel_prompt="SENTINEL-PROMPT-9f2a41-DO-NOT-EGRESS"
  sentinel_toolresult="SENTINEL-TOOLRESULT-4c81be-DO-NOT-EGRESS"
  t16_proj="$st_root/t16/project"
  mkdir -p "$t16_proj"
  t16_sid="t16-session"
  t16_transcript="$t16_proj/transcript.jsonl"
  _st_write_sentinel_transcript "$t16_transcript" "$sentinel_prompt" "$sentinel_toolresult"
  _st_write_posture "$t16_proj" "shadow"
  t16_run_dir="$t16_proj/.ravenclaude/runs/$t16_sid"

  rc16=0
  CLAUDE_PROJECT_DIR="$t16_proj" bash "$script_self" --event prompt \
    <<< "{\"session_id\":\"$t16_sid\",\"transcript_path\":\"$t16_transcript\"}" \
    >/dev/null 2>&1 || rc16=$?

  leak16=""
  if [ -d "$t16_run_dir" ]; then
    leak16="$(grep -rl -e "$sentinel_prompt" -e "$sentinel_toolresult" "$t16_run_dir" 2>/dev/null || true)"
  fi
  if [ "$rc16" -eq 0 ] && [ -z "$leak16" ]; then
    _ok "no-egress: neither the planted prompt sentinel nor the tool-result sentinel appear anywhere under the run dir (hook-events.jsonl, caveman-route.jsonl, or the state file)"
  else
    _fail "no-egress: expected NO sentinel leakage under $t16_run_dir, found: ${leak16:-<n/a, rc=$rc16>}"
  fi

  # ---- Test 17 (must-fail half): a mutant that echoes a raw transcript
  # slice into the route-log entry (a hypothetical C8 regression) DOES leak
  # a sentinel -- proving the grep above is capable of catching a real
  # leak, not just passing on an untested absence. Control: the REAL
  # script, identical fixture, fresh session id -> still no leak. ----------
  local t17_root mutant17_dir mutant17_engine t17_sid t17_real_sid rc17a rc17b \
        mutant17_run_dir real17_run_dir mutant17_leak real17_leak
  t17_root="$st_root/t17"
  mutant17_dir="$t17_root/mutant-scripts"
  mkdir -p "$mutant17_dir"

  mutant17_engine="$mutant17_dir/caveman-route-engine.py"
  python3 - "$plugin_root/scripts/caveman-route-engine.py" "$mutant17_engine" <<'PYEOF'
import sys
src_path, dst_path = sys.argv[1], sys.argv[2]
src = open(src_path, encoding="utf-8").read()
anchor = "    try:\n        _append_route_log(log_path, entry)"
if anchor not in src:
    raise SystemExit("MUTANT-BUILD-FAILED: anchor line not found -- engine source drifted")
leak_line = (
    "    entry[\"_debug_raw_tail\"] = open(transcript_path, \"r\", "
    "encoding=\"utf-8\", errors=\"replace\").read()[-4000:]  "
    "# MUTANT: raw transcript egress (C8 regression)\n"
)
patched = src.replace(anchor, leak_line + anchor, 1)
open(dst_path, "w", encoding="utf-8").write(patched)
PYEOF
  cp "$plugin_root/scripts/caveman-route.py" "$mutant17_dir/caveman-route.py"

  t17_sid="t17-mutant-session"
  mutant17_run_dir="$t16_proj/.ravenclaude/runs/$t17_sid"
  rc17a=0
  CLAUDE_PROJECT_DIR="$t16_proj" python3 "$mutant17_engine" --event prompt \
    <<< "{\"session_id\":\"$t17_sid\",\"transcript_path\":\"$t16_transcript\"}" \
    >/dev/null 2>&1 || rc17a=$?
  mutant17_leak=""
  if [ -d "$mutant17_run_dir" ]; then
    mutant17_leak="$(grep -rl -e "$sentinel_prompt" -e "$sentinel_toolresult" "$mutant17_run_dir" 2>/dev/null || true)"
  fi
  if [ -n "$mutant17_leak" ]; then
    _ok "must-fail-half (mutant): raw-transcript-echo mutant DOES leak a sentinel into $mutant17_leak -- proves the no-egress grep is capable of catching a real leak"
  else
    _fail "must-fail-half (mutant): expected the raw-echo mutant to leak a sentinel, found none -- the teeth test itself is broken (rc=$rc17a)"
  fi

  t17_real_sid="t17-real-session"
  real17_run_dir="$t16_proj/.ravenclaude/runs/$t17_real_sid"
  rc17b=0
  CLAUDE_PROJECT_DIR="$t16_proj" bash "$script_self" --event prompt \
    <<< "{\"session_id\":\"$t17_real_sid\",\"transcript_path\":\"$t16_transcript\"}" \
    >/dev/null 2>&1 || rc17b=$?
  real17_leak=""
  if [ -d "$real17_run_dir" ]; then
    real17_leak="$(grep -rl -e "$sentinel_prompt" -e "$sentinel_toolresult" "$real17_run_dir" 2>/dev/null || true)"
  fi
  if [ "$rc17b" -eq 0 ] && [ -z "$real17_leak" ]; then
    _ok "no-egress gate (real script): identical fixture, fresh session -> still no sentinel leak (control: 17's mutant proves the gate is what prevents it)"
  else
    _fail "no-egress gate (real script): expected no leak, found: ${real17_leak:-<n/a, rc=$rc17b>}"
  fi

  echo
  if [ "$_ST_FAIL" -eq 0 ]; then
    echo "caveman-route-hook.sh self-test: PASS (${_ST_PASS}/${_ST_TOTAL})"
  else
    echo "caveman-route-hook.sh self-test: FAIL (${_ST_PASS}/${_ST_TOTAL})"
  fi
  return "$_ST_FAIL"
}

# ---- top-level dispatch -----------------------------------------------------

if [ "${1:-}" = "--self-test" ]; then
  cmd_self_test
  exit $?
fi

if [ "${1:-}" = "--event" ]; then
  _run_hook "${2:-prompt}"
  exit 0
fi

# No recognized argument -> behave as a no-op, fail-open hook call (never a
# hard error; SessionStart/UserPromptSubmit invocations always pass --event).
_run_hook "prompt"
exit 0
