#!/usr/bin/env bash
# thing-orchestrator.sh — the "Lawspeaker" of the command-review tribunal ("the Thing").
#
# A PreToolUse(Bash) hook. When command review is toggled ON for a command's
# comfort-posture category, it convenes the tribunal — in T3, a PANEL of up to
# three reviewer seats (Forseti/security, Mímir/correctness, Heimdall/injection)
# plus Thor (tie-breaker, convened only on a split or low-confidence panel) —
# renders ALLOW / DENY / EDIT, writes an audit-trail ("Sága log") entry, and
# returns a Claude Code permission verdict.
#
# Protocol (code.claude.com/docs/en/hooks, re-verified 2026-05-25):
#   - stdin is the tool call as JSON: {tool_name, tool_input, cwd, session_id, ...}
#   - On exit 0 we emit hookSpecificOutput.permissionDecision (allow|deny|ask)
#     and, on EDIT, updatedInput:{command:<revised>} alongside an "allow".
#     (deny blocks even under --dangerously-skip-permissions; allow resolves an
#      "ask" to a run; allow can NOT loosen a settings `deny` floor.)
#   - The platform FAILS OPEN on hook timeout, so the panel deadline below is
#     OUR job — we emit our own verdict before the hook `timeout` (90s) fires.
#
# Routing + config + the deterministic concern screen come from
# scripts/thing-decision.py (which calls scripts/thing-concerns.py) in ONE call.
#
# Fail-closed posture (never silently allow on our own error):
#   - missing jq / decision helper      -> deny  (E14: detect-and-deny)
#   - present-but-malformed thing.yaml  -> ask
#   - panel abstains / errors           -> per-category timeout posture
#                                          (deny for the high-stakes categories,
#                                           ask for shell_readonly)
# A command in NO enabled category falls through (exit 0, no output) to the
# normal comfort-posture flow — that flow is the safety floor.

set -euo pipefail

# ── Structured hook-event substrate (Phase 0). Source the emit helper so every
#    deny path below can call _emit_hook_event. Fail-safe: a missing helper
#    becomes a no-op stub so the emit calls can never throw or block the verdict.
_emit_event_helper="$(dirname "${BASH_SOURCE[0]}")/_emit-event.sh"
if [ -f "$_emit_event_helper" ]; then
  # shellcheck source=/dev/null
  . "$_emit_event_helper" 2>/dev/null || true
fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

# ── Recursion guard: a seat runs `claude -p` (which we mark THING_SEAT_ACTIVE);
#    belt-and-suspenders so a tribunal call can never reconvene the tribunal. ──
[ -n "${THING_SEAT_ACTIVE:-}" ] && exit 0

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
DECISION="${PLUGIN_ROOT}/scripts/thing-decision.py"
CONCERNS="${PLUGIN_ROOT}/scripts/thing-concerns.py"
SEAT="${PLUGIN_ROOT}/scripts/thing-seat.sh"

# Read the tool call from stdin (canonical contract).
payload=""
if [ ! -t 0 ]; then payload="$(cat)"; fi
[ -z "$payload" ] && exit 0

# ── Emit a Claude Code PreToolUse verdict and exit. ───────────────────────────
emit() {  # emit <allow|deny|ask> <reason>
  jq -cn --arg d "$1" --arg r "$2" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:$d,permissionDecisionReason:$r}}'
  exit 0
}
emit_edit() {  # emit_edit <revised-command> <reason>
  jq -cn --arg c "$1" --arg r "$2" \
    '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"allow",permissionDecisionReason:$r,updatedInput:{command:$c}}}'
  exit 0
}

# jq is required to read the payload at all. If it is missing we cannot even
# parse stdin — detect-and-deny rather than fail open (design E14).
if ! command -v jq >/dev/null 2>&1; then
  echo "[Command review] jq not available; blocking to fail closed." >&2
  _emit_hook_event "thing-orchestrator.sh" "deny" "Bash" "" "jq-missing-fail-closed" 2
  exit 2
fi

tool_name="$(printf '%s' "$payload" | jq -r '.tool_name // empty')"
# Track B: review the tool shapes the Thing handles; anything else → normal flow.
# (The hooks.json matcher already filters to these; this is defense-in-depth so a
# direct/odd invocation can't reach the per-shape extraction below.)
case "$tool_name" in
  Bash | Read | Write | Edit | MultiEdit | WebFetch | WebSearch | mcp__*) ;;
  *) exit 0 ;;
esac

cwd="$(printf '%s' "$payload" | jq -r '.cwd // empty')"
[ -z "$cwd" ] && cwd="$PWD"
session_id="$(printf '%s' "$payload" | jq -r '.session_id // empty')"

# ── Fast short-circuit: if no category is toggled on, do nothing. Runs BEFORE any
#    per-shape extraction or python call, so an opted-out consumer pays nothing
#    (one grep) regardless of tool shape — incl. a Write with no posture file. ──
posture_file="${cwd}/.ravenclaude/comfort-posture.yaml"
# NOTE: do NOT "optimize" this grep to also parse `enabled:` from command_review.
# The self-disable + hard-rule floors (§B.9.5, §B.9.3) must run whenever ANY
# category is toggled on, regardless of command_review.enabled. Suppressing the
# short-circuit here to avoid a python call would silently remove those floors for
# consumers who have categories toggled on but set enabled: false.
if [ ! -f "$posture_file" ] || ! grep -Eq '^[[:space:]]*thing:[[:space:]]*(on|true|yes)\b' "$posture_file"; then
  exit 0
fi

# ── Routing + config. Fail CLOSED (deny), not ask: past the short-circuit a
# category is toggled on — the user opted into gating; a missing/silent engine
# can't distinguish a high-stakes mutation from a read, so deny (assessment #7).
if [ ! -f "$DECISION" ]; then
  _emit_hook_event "thing-orchestrator.sh" "deny" "$tool_name" "" "decision-helper-missing" 2
  emit deny "Command review is enabled but its decision helper is missing (broken install). Failing closed. Fix the plugin install, or turn command review off in the comfort-posture dashboard."
fi

# Bash classifies via the command string (UNCHANGED path); every other shape
# classifies the whole tool-call payload via classify-payload (JSON on stdin).
if [ "$tool_name" = "Bash" ]; then
  cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty')"
  [ -z "$cmd" ] && exit 0
  payload_shape="command"
  decision="$(THING_SEAT_ACTIVE= python3 "$DECISION" --root "$cwd" classify "$cmd" 2>/dev/null || true)"
else
  cmd=""
  decision="$(printf '%s' "$payload" | THING_SEAT_ACTIVE= python3 "$DECISION" --root "$cwd" classify-payload 2>/dev/null || true)"
  payload_shape="$(printf '%s' "$decision" | jq -r '.payload_shape // "command"')"
fi
if [ -z "$decision" ]; then
  _emit_hook_event "thing-orchestrator.sh" "deny" "$tool_name" "$cmd" "classification-failed" 2
  emit deny "Command review could not classify the tool call (decision helper failed). Failing closed. Re-run, fix the install, or turn command review off in the dashboard."
fi

enabled="$(printf '%s' "$decision" | jq -r '.thing_enabled // false')"
category="$(printf '%s' "$decision" | jq -r '.category // "unknown"')"
reviewed="$(printf '%s' "$decision" | jq -r '.reviewed_text // empty')"

# §Serialization — per-shape Sága tool_input + cache identity. Bash keeps the
# exact prior {command} / command-string forms (byte-identical Sága + cache);
# other shapes use the shape-appropriate forms from classify-payload.
if [ "$tool_name" = "Bash" ]; then
  saga_ti="$(jq -cn --arg c "$cmd" '{command:$c}')"
  cache_id="$cmd"
else
  saga_ti="$(printf '%s' "$decision" | jq -c '.saga_tool_input // {command:""}')"
  cache_id="$(printf '%s' "$decision" | jq -r '.cache_identity // empty')"
fi

# §Fail-open: a non-Bash shape that matched the hook but did NOT classify (e.g. a
# future matcher entry with no classify_payload case) fails CLOSED. We are past
# the short-circuit, so the Thing is active; an unmappable matched shape is a
# config/code error, not a free pass.
if [ "$tool_name" != "Bash" ] && { [ -z "$category" ] || [ "$category" = "null" ] || [ "$category" = "unknown" ]; }; then
  _emit_hook_event "thing-orchestrator.sh" "deny" "$tool_name" "" "unmapped-shape" 2
  emit deny "Command review: DENIED — could not classify this ${tool_name} tool call (unmapped shape). Failing closed."
fi

# ── §B.9.5: the Thing cannot disable itself. This guard is CATEGORY-INDEPENDENT
#    — it fires whenever ANY category is toggled on (we are past the short-circuit
#    above), even if THIS command's own category is off — because disabling the
#    Thing affects every category. Pre-LLM, unilateral DENY; no seat convened.
#    Closes the evasion where a self-disabling command is shaped to classify into
#    a category whose toggle happens to be off. ────────────────────────────────
self_disable="$(printf '%s' "$decision" | jq -r '.self_disable_deny // false')"
if [ "$self_disable" = "true" ]; then
  sd_concern="$(printf '%s' "$decision" | jq -r '.self_disable_concern // "xc.tribunal-self-disable"')"
  sd_run_id="thing-$(date -u +%Y-%m-%dT%H-%M-%SZ)-$$"
  sd_audit="${cwd}/.ravenclaude/runs/thing"  # config audit_dir is resolved later
  if mkdir -p "$sd_audit" 2>/dev/null; then
    jq -cn --arg id "$sd_run_id" --arg sid "$session_id" \
      --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --argjson ti "$saga_ti" --arg tn "$tool_name" \
      --arg cat "$category" --arg concern "$sd_concern" \
      '{id:$id,session_id:$sid,timestamp:$ts,tool_name:$tn,
        tool_input:$ti,category:$cat,phase:"T4-self-disable",
        seats:[],concerns_cited:[$concern],final_verdict:"deny",
        updated_input:null,duration_ms:0}' \
      > "${sd_audit}/${sd_run_id}.json" 2>/dev/null || true
  fi
  _emit_hook_event "thing-orchestrator.sh" "deny" "$tool_name" "$cmd" "self-disable" 2
  emit deny "Command review (the Thing): DENIED — this command would disable or tamper with the Thing itself (${sd_concern}). Refused unilaterally (§B.9.5); turn the Thing off in the comfort-posture dashboard instead. Sága log: .ravenclaude/runs/thing/${sd_run_id}.json"
fi

# ── Maintainer-substrate exemption audit (dev-repo only). ────────────────────
# When thing-decision.py sets maintainer_substrate_exempt=true, the substrate-path
# self-disable was suppressed (the edit falls through to the normal panel). Log WHY
# the substrate edit wasn't denied — audit trail for post-PR security review. This
# block DOES NOT alter any verdict; it only writes a Sága entry and continues.
# The hard-rule floor (§B.9.3, above) still runs first, and force-push / curl|sh
# are denied before we ever reach here.
maint_exempt="$(printf '%s' "$decision" | jq -r '.maintainer_substrate_exempt // false')"
if [ "$maint_exempt" = "true" ]; then
  maint_owner="$(printf '%s' "$decision" | jq -r '.maintainer_substrate_exempt_owner // "unknown"')"
  maint_run_id="thing-$(date -u +%Y-%m-%dT%H-%M-%SZ)-$$-exempt"
  maint_audit="${cwd}/.ravenclaude/runs/thing"
  if mkdir -p "$maint_audit" 2>/dev/null; then
    jq -cn --arg id "$maint_run_id" --arg sid "$session_id" \
      --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --argjson ti "$saga_ti" --arg tn "$tool_name" \
      --arg cat "$category" --arg owner "$maint_owner" \
      '{id:$id,session_id:$sid,timestamp:$ts,tool_name:$tn,
        tool_input:$ti,category:$cat,phase:"maintainer-substrate-exempt",
        maintainer_substrate_exempt:true,gh_repo_owner:$owner,
        seats:[],concerns_cited:[],final_verdict:"panel-pending",
        updated_input:null,duration_ms:0}' \
      > "${maint_audit}/${maint_run_id}.json" 2>/dev/null || true
  fi
  # Do NOT emit here — fall through to the normal panel below.
fi

# ── §B.9.3: unarguable hard-deny rules (force-push to a protected branch, curl|sh)
#    are CATEGORY-INDEPENDENT too — `always_screen` in the catalog. They fire
#    whenever ANY category is toggled, even if THIS command classifies into an
#    untoggled category or None, so a wrapped / mis-routed form
#    (`nice git push --force`, `git status && git push --force`) cannot dodge the
#    hard DENY. Pre-LLM, unilateral; no seat convened. ──────────────────────────
hard_rule="$(printf '%s' "$decision" | jq -r '.hard_rule_deny // false')"
if [ "$hard_rule" = "true" ]; then
  hr_concern="$(printf '%s' "$decision" | jq -r '.hard_rule_concern // "hard rule"')"
  hr_run_id="thing-$(date -u +%Y-%m-%dT%H-%M-%SZ)-$$"
  hr_audit="${cwd}/.ravenclaude/runs/thing"
  if mkdir -p "$hr_audit" 2>/dev/null; then
    jq -cn --arg id "$hr_run_id" --arg sid "$session_id" \
      --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --argjson ti "$saga_ti" --arg tn "$tool_name" \
      --arg cat "$category" --arg concern "$hr_concern" \
      '{id:$id,session_id:$sid,timestamp:$ts,tool_name:$tn,
        tool_input:$ti,category:$cat,phase:"hard-rule-deny",
        seats:[],concerns_cited:[$concern],final_verdict:"deny",
        updated_input:null,duration_ms:0}' \
      > "${hr_audit}/${hr_run_id}.json" 2>/dev/null || true
  fi
  _emit_hook_event "thing-orchestrator.sh" "deny" "$tool_name" "$cmd" "hard-rule-deny" 2
  emit deny "Command review (the Thing): DENIED — this command matches an unarguable hard rule (${hr_concern}) and is refused pre-LLM, regardless of which category routed it (§B.9.3). Sága log: .ravenclaude/runs/thing/${hr_run_id}.json"
fi

[ "$enabled" != "true" ] && exit 0   # category not toggled on -> normal flow

# §Payload caps: a reviewed payload too large to screen in full fails CLOSED.
if [ "$(printf '%s' "$decision" | jq -r '.payload_too_large // false')" = "true" ]; then
  _emit_hook_event "thing-orchestrator.sh" "deny" "$tool_name" "$cmd" "payload-too-large" 2
  emit deny "Command review (the Thing): DENIED — the ${payload_shape} payload exceeds the screening size limit and cannot be fully reviewed. Failing closed."
fi

config_error="$(printf '%s' "$decision" | jq -r '.config_error // empty')"
[ -n "$config_error" ] && emit ask "Command review config error ($config_error); deferring to you."

threshold="$(printf '%s' "$decision" | jq -r '.confidence_threshold // 0.5')"
seat_timeout="$(printf '%s' "$decision" | jq -r '.seat_timeout_seconds // 45')"
panel_deadline="$(printf '%s' "$decision" | jq -r '.panel_deadline_seconds // 75')"
audit_dir_rel="$(printf '%s' "$decision" | jq -r '.audit_dir // ".ravenclaude/runs/thing"')"
posture="$(printf '%s' "$decision" | jq -r '.timeout_posture // "ask"')"  # deny|ask
# §A1 dev-repo lockout fix: in the verified maintainer dev-repo context (the engine
# sets dev_repo_abstain_downgrade only after the dev_repo_exempt + gh-owner +
# marketplace.json AND-gate passes), an abstaining/inconclusive panel defers to the
# human instead of failing closed — an abstain there is a `claude -p` cold-start
# latency artifact, not a security signal. This downgrades ONLY the abstain/
# inconclusive posture (deny->ask); the hard-rule floor, self-disable guard,
# injection DENY, and secret-egress backstop all resolve before this branch and are
# untouched. It can never turn a deny into an allow.
posture_phrase="failing ${posture}"
abstain_downgrade="$(printf '%s' "$decision" | jq -r '.dev_repo_abstain_downgrade // false')"
if [ "$abstain_downgrade" = "true" ] && [ "$posture" = "deny" ]; then
  posture="ask"
  posture_phrase="deferring to you (maintainer dev-repo: an abstain here is a latency artifact, not a security signal — DENY downgraded to ASK)"
fi
pre_llm_deny="$(printf '%s' "$decision" | jq -r '.pre_llm_deny // false')"
deny_concern="$(printf '%s' "$decision" | jq -r '.deny_concern // empty')"
convened="$(printf '%s' "$decision" | jq -r '.convened_seats[]?' )"
screen_concerns="$(printf '%s' "$decision" | jq -c '.concerns // []')"
# T5 tier model: the tier drives the panel + the human-gate behavior. NOTE: jq's
# `//` treats BOTH null and `false` as empty, so `.panel_required // true` would
# wrongly yield "true" for a clean read (panel_required:false). Test == false
# explicitly; absent/null defaults to "true" (fail toward convening the panel).
panel_required="$(printf '%s' "$decision" | jq -r 'if .panel_required == false then "false" else "true" end')"
is_read="$(printf '%s' "$decision" | jq -r '.is_read // false')"
gate_allow="$(printf '%s' "$decision" | jq -r '.gate_allow // false')"
high_blast="$(printf '%s' "$decision" | jq -r '.high_blast // false')"
tier="$(printf '%s' "$decision" | jq -r '.tier // "unknown"')"
gate_floor="$(printf '%s' "$decision" | jq -r '.gate_floor // "high"')"
# #15 cost/UX knobs. The deterministic screen above already ran; these only let us
# skip the EXPENSIVE panel. bypass_match already excludes a critical screen.
bypass_match="$(printf '%s' "$decision" | jq -r '.bypass_match // false')"
cache_ttl="$(printf '%s' "$decision" | jq -r '.cache_ttl_seconds // 0')"
fatigue_threshold="$(printf '%s' "$decision" | jq -r '.fatigue_threshold // 0')"
config_hash="$(printf '%s' "$decision" | jq -r '.config_hash // empty')"

run_id="thing-$(date -u +%Y-%m-%dT%H-%M-%SZ)-$$"
started_ms="$(date +%s%3N 2>/dev/null || echo 0)"

# Per-seat parsed verdicts (associative arrays keyed by role).
declare -A SV SCONF SINJ SCITED SEDIT SREASON SSTATUS
seats_run=()

# Run one seat: writes verdict JSON to $tmp/$role.json, rc to $tmp/$role.rc.
run_seat() {  # run_seat <role> <model> <tmp> [peer_verdicts_json] [fallback_exclude_csv]
  local role="$1" model="$2" tmp="$3" peers="${4:-}" fb_exclude="${5:-}" out rc=0
  # Bash: THING_CMD (unchanged path). Non-Bash: THING_PAYLOAD (the reviewed text)
  # + THING_PAYLOAD_SHAPE. The full-payload secret screen already ran in
  # classify-payload, and the seat re-caps to SEAT_MAX_BYTES.
  if [ "$payload_shape" = "command" ]; then
    out="$(THING_SEAT_ACTIVE=1 THING_CMD="$cmd" THING_CATEGORY="$category" \
           THING_SEAT_ROLE="$role" THING_MODEL="$model" THING_PEER_VERDICTS="$peers" \
           MODEL_FALLBACK_EXCLUDE="$fb_exclude" \
           THING_SEAT_MOCK_VERDICT="${THING_SEAT_MOCK_VERDICT:-}" \
           timeout "${seat_timeout}s" bash "$SEAT" 2>/dev/null)" || rc=$?
  else
    out="$(THING_SEAT_ACTIVE=1 THING_PAYLOAD="$reviewed" THING_PAYLOAD_SHAPE="$payload_shape" \
           THING_CATEGORY="$category" \
           THING_SEAT_ROLE="$role" THING_MODEL="$model" THING_PEER_VERDICTS="$peers" \
           MODEL_FALLBACK_EXCLUDE="$fb_exclude" \
           THING_SEAT_MOCK_VERDICT="${THING_SEAT_MOCK_VERDICT:-}" \
           timeout "${seat_timeout}s" bash "$SEAT" 2>/dev/null)" || rc=$?
  fi
  printf '%s' "$out" > "$tmp/$role.json"
  printf '%s' "$rc" > "$tmp/$role.rc"
}

# Parse a finished seat's output into the per-seat arrays (status voted|abstain).
parse_seat() {  # parse_seat <role> <tmp>
  local role="$1" tmp="$2" out rc
  out="$(cat "$tmp/$role.json" 2>/dev/null || true)"
  rc="$(cat "$tmp/$role.rc" 2>/dev/null || echo 1)"
  if [ "$rc" != "0" ] || [ -z "$out" ] || ! printf '%s' "$out" | jq -e . >/dev/null 2>&1; then
    SSTATUS[$role]="abstain"; SV[$role]="abstain"; SCONF[$role]="0"
    SINJ[$role]="false"; SCITED[$role]="[]"; SEDIT[$role]="null"; SREASON[$role]=""
    return
  fi
  SSTATUS[$role]="voted"
  SV[$role]="$(printf '%s' "$out" | jq -r '.verdict // "abstain"')"
  SCONF[$role]="$(printf '%s' "$out" | jq -r '.confidence // 0')"
  SINJ[$role]="$(printf '%s' "$out" | jq -r '.injection_detected // false')"
  SCITED[$role]="$(printf '%s' "$out" | jq -c '.concerns_cited // []')"
  SEDIT[$role]="$(printf '%s' "$out" | jq -r '.edited_command // empty')"
  # Bound + strip control chars (assessment #13): a seat's reasoning is surfaced
  # into the user banner (esp. Thor's) and the Sága log. A prompt-injected seat
  # could return an over-long or newline/escape-laden string; cap at 200 chars and
  # drop control bytes at the source so every downstream use is already safe.
  SREASON[$role]="$(printf '%s' "$out" | jq -r '.reasoning // ""' | tr -d '\000-\037' | cut -c1-200)"
  # ── Resolved-false concern strip (v0.97+). The orchestrator already
  #    deterministically resolves some concerns before the panel runs (e.g. the
  #    category `file_edit_project` proves the target path is INSIDE the tree —
  #    the seat envelope is told this, but if a seat still cites
  #    xc.outside-project-tree we strip it as a confirmed false positive). If
  #    the seat's deny was based SOLELY on the stripped concern, downgrade to
  #    abstain so the abstain-gate (and dev_repo_exempt's abstain-downgrade)
  #    catch it instead of a confident-but-wrong deny carrying. Real denies that
  #    cite other concerns alongside are unaffected.
  local orig_cited="${SCITED[$role]}"
  local stripped_cited="$orig_cited"
  if [ "$category" = "file_edit_project" ]; then
    stripped_cited="$(printf '%s' "$orig_cited" | jq -c 'map(select(. != "xc.outside-project-tree"))')"
  fi
  if [ "$stripped_cited" != "$orig_cited" ]; then
    SCITED[$role]="$stripped_cited"
    local removed
    removed="$(jq -cn --argjson o "$orig_cited" --argjson s "$stripped_cited" '$o - $s')"
    RESOLVED_STRIPS="$(jq -cn --argjson a "${RESOLVED_STRIPS:-[]}" --arg seat "$role" --argjson removed "$removed" \
      '$a + [{seat:$seat, removed:$removed, reason:"category=file_edit_project proves in-tree"}]')"
    if [ "${SV[$role]}" = "deny" ] && [ "$(printf '%s' "$stripped_cited" | jq -r 'length')" = "0" ]; then
      SSTATUS[$role]="abstain"; SV[$role]="abstain"
    fi
  fi
}

verdict="ask"; reason=""; revised=""; final_cited="$screen_concerns"
phase="T3-panel"

# ── #15 verdict cache (precompute). Keyed by command + category + config_hash so a
#    rules/catalog change invalidates it; TTL-bounded. The hard-rule screen above
#    always ran, so only the EXPENSIVE panel result is ever served from cache. ──
cache_dir="${cwd}/${audit_dir_rel}/cache"
cache_hit="false"; cache_verdict=""; cache_revised=""
if [ "${cache_ttl:-0}" -gt 0 ] && [ -n "$config_hash" ] && command -v sha256sum >/dev/null 2>&1; then
  cache_key="$(printf '%s' "${cache_id}|${category}|${config_hash}" | sha256sum | cut -d' ' -f1)"
  cache_file="${cache_dir}/${cache_key}.json"
  if [ -f "$cache_file" ]; then
    c_ts="$(jq -r '.ts // 0' "$cache_file" 2>/dev/null || echo 0)"
    now_ts="$(date +%s 2>/dev/null || echo 0)"
    if [ "$c_ts" -gt 0 ] && [ $(( now_ts - c_ts )) -lt "$cache_ttl" ]; then
      cache_verdict="$(jq -r '.verdict // empty' "$cache_file" 2>/dev/null || true)"
      cache_revised="$(jq -r '.revised // empty' "$cache_file" 2>/dev/null || true)"
      [ -n "$cache_verdict" ] && cache_hit="true"
    fi
  fi
fi

if [ "$pre_llm_deny" = "true" ]; then
  # ── Deterministic hard-rule denial — no seat convened (design §B.9.3). ──────
  verdict="deny"
  reason="Command review (the Thing): DENIED before review — matched unarguable critical concern ${deny_concern}."
  phase="T3-pre-screen"
elif [ "$panel_required" != "true" ]; then
  # ── Clean low-risk read (T5 tier model): the zero-cost deterministic screen
  #    found nothing, so no LLM panel is convened. Reads are never surfaced to
  #    you; a clean one auto-allows. (An escalated read DOES convene a panel — it
  #    falls through to the branch below — and is auto-decided, never asked.) ──
  verdict="allow"
  reason="Command review: low-risk read (tier ${tier}) cleared by the deterministic screen; no panel convened."
  phase="T5-clean-read"
elif [ "$bypass_match" = "true" ]; then
  # ── #15 bypass-list: the user explicitly trusts this pattern. The hard-rule
  #    screen already passed (not pre_llm_deny; bypass excludes critical), so
  #    auto-allow without convening the panel. ──────────────────────────────────
  verdict="allow"
  reason="Command review: matched your command_review.bypass list — auto-allowed without convening the panel (the deterministic hard-rule screen still ran and was clean)."
  phase="T5-bypass"
elif [ "$cache_hit" = "true" ]; then
  # ── #15 cache hit: reuse a recent panel verdict for an identical command under
  #    the same config (TTL + config_hash bounded). The hard-rule screen re-ran. ─
  verdict="$cache_verdict"; revised="$cache_revised"
  reason="Command review: reusing a cached panel verdict (${verdict}) for an identical command within the ${cache_ttl}s cache window; no panel re-convened."
  phase="T5-cache-hit"
else
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT

  # ── Fan the convened seats out in PARALLEL, bounded by the panel deadline. ──
  pids=()
  for role in $convened; do
    model="$(printf '%s' "$decision" | jq -r --arg r "$role" '.panel[$r].model // "claude-haiku-4-5"')"
    # Peer-exclude: the OTHER convened seats' models. Passed to the seat's
    # model-fallback so a fallback never lands on a peer's model — preserving the
    # >=2-distinct-backbone diversity invariant BY CONSTRUCTION (no post-hoc
    # cross-seat re-check). Empty when fallback is off; harmless then.
    peer_excl=""
    for other in $convened; do
      [ "$other" = "$role" ] && continue
      om="$(printf '%s' "$decision" | jq -r --arg r "$other" '.panel[$r].model // empty')"
      [ -n "$om" ] && peer_excl="${peer_excl}${peer_excl:+,}$om"
    done
    seats_run+=("$role")
    run_seat "$role" "$model" "$tmp" "" "$peer_excl" &
    pids+=("$!")
  done
  if [ "${#pids[@]}" -gt 0 ]; then
    # The watchdog enforces the panel-level hard deadline by killing straggler
    # seats. Its fds are detached from the hook's stdout — otherwise the
    # backgrounded `sleep` would inherit the verdict pipe and a command-
    # substitution caller would block for the full deadline even after the
    # verdict is emitted. `setsid` (when available) puts the sleep in its own
    # session so killing the watchdog reaps the sleep too.
    if command -v setsid >/dev/null 2>&1; then
      setsid bash -c 'sleep "$1"; shift; for p in "$@"; do kill "$p" 2>/dev/null || true; done' \
        _ "$panel_deadline" "${pids[@]}" </dev/null >/dev/null 2>&1 &
    else
      ( sleep "$panel_deadline"; for p in "${pids[@]}"; do kill "$p" 2>/dev/null || true; done ) \
        </dev/null >/dev/null 2>&1 &
    fi
    watchdog=$!
    for p in "${pids[@]}"; do wait "$p" 2>/dev/null || true; done
    kill "$watchdog" 2>/dev/null || true
    wait "$watchdog" 2>/dev/null || true
  fi
  for role in $convened; do parse_seat "$role" "$tmp"; done

  # ── Aggregate (design §B.3.2). ──────────────────────────────────────────────
  n_convened=0; n_abstain=0; any_injection="false"; low_conf="false"
  declare -A seen_verdict
  all_cited="[]"
  for role in $convened; do
    n_convened=$((n_convened + 1))
    if [ "${SSTATUS[$role]}" = "abstain" ]; then
      n_abstain=$((n_abstain + 1)); continue
    fi
    [ "${SINJ[$role]}" = "true" ] && any_injection="true"
    awk -v c="${SCONF[$role]}" -v t="$threshold" 'BEGIN{exit !(c < t)}' && low_conf="true"
    seen_verdict[${SV[$role]}]=1
    all_cited="$(jq -cn --argjson a "$all_cited" --argjson b "${SCITED[$role]}" '$a + $b')"
  done

  has_critical="false"
  # 1. Abstention gate: >=2 abstained, or the whole convened panel abstained.
  if [ "$n_abstain" -ge 2 ] || { [ "$n_convened" -gt 0 ] && [ "$n_abstain" -eq "$n_convened" ]; }; then
    verdict="$posture"
    reason="Command review: the panel abstained (timeout or error); ${posture_phrase} for ${category}."
  # 2. Injection override (unilateral DENY).
  elif [ "$any_injection" = "true" ]; then
    verdict="deny"
    reason="Command review: DENIED — prompt-injection detected."
    final_cited="$all_cited"
  else
    # Critical-concern severity (for the backstop below). A cited critical means
    # ALLOW is off the table (design §A.4) — but a valid EDIT that REMOVES the
    # critical is permitted, so the veto is applied only to an ALLOW outcome,
    # after EDIT re-validation, not as a pre-empting branch here.
    cited_ids="$(printf '%s' "$all_cited" | jq -r '.[]' 2>/dev/null | paste -sd, - || true)"
    if [ -n "$cited_ids" ] && [ -f "$CONCERNS" ]; then
      has_critical="$(THING_SEAT_ACTIVE= python3 "$CONCERNS" severity --ids "$cited_ids" 2>/dev/null \
                      | jq -r '.has_critical // false' 2>/dev/null || echo false)"
    fi
    # Distinct non-abstain verdicts -> split. Low confidence -> escalate too.
    n_distinct="${#seen_verdict[@]}"
    escalate="false"
    { [ "$n_distinct" -gt 1 ] || [ "$low_conf" = "true" ]; } && escalate="true"

    if [ "$escalate" = "true" ]; then
      # 4. Convene Thor on the reasoning chains of the convened seats.
      peers="$(for role in $convened; do
                 [ "${SSTATUS[$role]}" = "voted" ] && jq -cn --arg r "$role" --arg v "${SV[$role]}" \
                   --argjson cf "${SCONF[$role]}" --argjson ci "${SCITED[$role]}" --arg rs "${SREASON[$role]}" \
                   '{seat:$r,verdict:$v,confidence:$cf,concerns_cited:$ci,reasoning:$rs}'
               done | jq -cs '.')"
      thor_model="$(printf '%s' "$decision" | jq -r '.panel.thor.model // "claude-opus-4-8"')"
      seats_run+=("thor")
      run_seat "thor" "$thor_model" "$tmp" "$peers"
      parse_seat "thor" "$tmp"
      tv="${SV[thor]}"
      final_cited="${SCITED[thor]}"
      if [ "${SSTATUS[thor]}" = "abstain" ]; then
        verdict="$posture"; reason="Command review: tie-breaker abstained; ${posture_phrase} for ${category}."
      elif [ "${SINJ[thor]}" = "true" ]; then
        verdict="deny"; reason="Command review: DENIED — tie-breaker detected injection. ${SREASON[thor]}"
      elif [ "$tv" = "edit" ]; then
        verdict="edit"; revised="${SEDIT[thor]}"; reason="Command review: tie-breaker EDIT. ${SREASON[thor]}"
      elif [ "$tv" = "deny" ]; then
        verdict="deny"; reason="Command review: DENIED by tie-breaker. ${SREASON[thor]}"
      else
        verdict="allow"; reason="Command review: ALLOWED by tie-breaker. ${SREASON[thor]}"
      fi
    else
      # 5. Unanimous (non-abstain) verdict among the convened seats.
      the_verdict=""
      for v in "${!seen_verdict[@]}"; do the_verdict="$v"; done
      case "$the_verdict" in
        allow) verdict="allow"; reason="Command review: ALLOWED." ;;
        deny)  verdict="deny";  reason="Command review: DENIED."; final_cited="$all_cited" ;;
        edit)
          verdict="edit"
          # Take the first convened seat's edit (by convening order).
          for role in $convened; do
            if [ "${SV[$role]}" = "edit" ] && [ -n "${SEDIT[$role]}" ] && [ "${SEDIT[$role]}" != "null" ]; then
              revised="${SEDIT[$role]}"; final_cited="${SCITED[$role]}"; break
            fi
          done
          reason="Command review: EDIT proposed." ;;
        *)     verdict="$posture"; reason="Command review: inconclusive; ${posture_phrase}." ;;
      esac
    fi
  fi

  # ── §EDIT coercion: file/network/MCP shapes are ALLOW/DENY-only v1 (decision 2)
  #    — there is no machine-checked concerns(revised) ⊆ concerns(original)
  #    invariant for non-command content, so a seat EDIT is coerced to DENY before
  #    the emit_edit path can ever be reached. ─────────────────────────────────
  if [ "$payload_shape" != "command" ] && [ "$verdict" = "edit" ]; then
    verdict="deny"
    revised=""
    reason="Command review: DENIED — EDIT is not supported for ${payload_shape} shapes (ALLOW/DENY only); a seat proposed a rewrite."
  fi

  # ── EDIT-safety invariant: re-validate the revision deterministically. ──────
  if [ "$verdict" = "edit" ]; then
    if [ -z "$revised" ] || [ "$revised" = "null" ]; then
      verdict="deny"; reason="Command review: DENIED — EDIT verdict carried no revised command."
    else
      cited_one="$(printf '%s' "$final_cited" | jq -r '.[0] // empty')"
      reval="$(THING_SEAT_ACTIVE= python3 "$CONCERNS" revalidate --category "$category" \
                --cited "${cited_one:-none}" --original "$cmd" --revised "$revised" 2>/dev/null || true)"
      ok="$(printf '%s' "$reval" | jq -r '.ok // false' 2>/dev/null || echo false)"
      if [ "$ok" != "true" ]; then
        verdict="deny"
        reason="Command review: DENIED — proposed EDIT failed the safety invariant ($(printf '%s' "$reval" | jq -r '.reason // "rejected"'))."
      fi
    fi
  fi

  # ── Critical-concern veto (backstop): a cited critical can never ALLOW. ─────
  if [ "$verdict" = "allow" ] && [ "${has_critical:-false}" = "true" ]; then
    verdict="deny"
    reason="Command review: DENIED — a critical concern was cited; ALLOW is not a permitted verdict (§A.4)."
    final_cited="$all_cited"
  fi
fi

# ── gate_floor (T5): surface a confident panel-ALLOW to you (ask) when the
#    command's tier is at/above the configured floor, OR when it is high-blast
#    (irreversible) regardless of floor. Reads are never surfaced. A DENY blocks
#    and an EDIT rewrites autonomously — only a plain ALLOW is gated, so the
#    tribunal still pre-filters the dangerous/fixable commands before you see one.
if [ "$verdict" = "allow" ] && [ "$is_read" != "true" ] \
   && { [ "$gate_allow" = "true" ] || [ "$high_blast" = "true" ]; }; then
  verdict="ask"
  if [ "$high_blast" = "true" ]; then
    reason="Command review: the tribunal found no blocker, but this is an irreversible (high-blast) action — surfacing for your confirmation. ${reason}"
  else
    reason="Command review: the tribunal found no blocker (tier ${tier} at/above your gate_floor ${gate_floor}); surfacing for your confirmation. ${reason}"
  fi
fi

# ── #15 session-fatigue counter (advisory ONLY — never relaxes the gate). Counts
#    the asks surfaced this session; past the threshold it appends a nudge toward
#    tuning gate_floor / adding a bypass. Per-session counter file. ─────────────
if [ "$verdict" = "ask" ] && [ "${fatigue_threshold:-0}" -gt 0 ] && [ -n "$session_id" ]; then
  safe_sid="$(printf '%s' "$session_id" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
  fdir="${cwd}/${audit_dir_rel}/fatigue"
  if [ -n "$safe_sid" ] && mkdir -p "$fdir" 2>/dev/null; then
    fcount=$(( $(cat "${fdir}/${safe_sid}" 2>/dev/null || echo 0) + 1 ))
    printf '%s' "$fcount" > "${fdir}/${safe_sid}" 2>/dev/null || true
    if [ "$fcount" -ge "$fatigue_threshold" ]; then
      reason="${reason} [Command review has asked ${fcount} times this session — consider raising gate_floor or adding a command_review.bypass entry via the dashboard.]"
    fi
  fi
fi

# ── Sága log (best-effort; never let a logging failure change the verdict). ───
audit_dir="${cwd}/${audit_dir_rel}"
ended_ms="$(date +%s%3N 2>/dev/null || echo 0)"
duration_ms=$(( ended_ms - started_ms ))
seats_json="[]"
for role in "${seats_run[@]:-}"; do
  [ -z "$role" ] && continue
  # Persist each seat's FULL verdict for forensics (assessment #18): verdict,
  # status, confidence, injection flag, cited concerns, the bounded reasoning,
  # and any proposed edit. jq --arg escapes the reasoning safely.
  seats_json="$(jq -cn --argjson a "$seats_json" \
    --arg name "$role" --arg v "${SV[$role]:-abstain}" --arg st "${SSTATUS[$role]:-abstain}" \
    --argjson cf "${SCONF[$role]:-0}" --arg inj "${SINJ[$role]:-false}" \
    --argjson ci "${SCITED[$role]:-[]}" \
    --arg rsn "${SREASON[$role]:-}" --arg ec "${SEDIT[$role]:-}" \
    '$a + [{name:$name,verdict:$v,status:$st,confidence:$cf,injection_detected:($inj=="true"),concerns_cited:$ci,reasoning:$rsn,edited_command:(if $ec=="" then null else $ec end)}]')"
done
# Write the Sága entry, capturing whether it actually persisted (assessment #10).
audit_written="false"
if mkdir -p "$audit_dir" 2>/dev/null && jq -cn \
    --arg id "$run_id" --arg sid "$session_id" \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --argjson ti "$saga_ti" --arg tn "$tool_name" --arg cat "$category" --arg phase "$phase" \
    --arg verdict "$verdict" --arg revised "$revised" \
    --argjson seats "$seats_json" --argjson concerns "${final_cited:-[]}" \
    --argjson strips "${RESOLVED_STRIPS:-[]}" \
    --argjson duration "${duration_ms:-0}" \
    '{id:$id,session_id:$sid,timestamp:$ts,tool_name:$tn,
      tool_input:$ti,category:$cat,phase:$phase,
      seats:$seats,concerns_cited:$concerns,final_verdict:$verdict,
      resolved_false_strips:$strips,
      updated_input:(if $revised=="" then null else {command:$revised} end),
      duration_ms:$duration}' \
    > "${audit_dir}/${run_id}.json" 2>/dev/null; then
  audit_written="true"
fi

# #10: a permissive verdict (allow/edit) with NO audit record is downgraded to a
# fail-closed DENY — never emit an unrecorded allow. A deny/ask needs no record to
# be safe, so those still emit.
if [ "$audit_written" != "true" ] && { [ "$verdict" = "allow" ] || [ "$verdict" = "edit" ]; }; then
  verdict="deny"; revised=""
  reason="Command review: the verdict could not be written to the Sága audit log, so the permissive result is downgraded to a fail-closed DENY (an allow requires an audit trail). Check write permissions on ${audit_dir_rel}. ${reason}"
fi

# ── #15 cache WRITE: persist a real PANEL verdict (allow/edit/deny) for reuse
#    within the TTL window. Skip the non-panel phases (bypass / cache-hit / clean
#    read / pre-screen / self-disable) and never cache an `ask`; only when the
#    audit actually persisted (so a cache entry always has a Sága counterpart). ─
case "$phase" in
  T5-bypass | T5-cache-hit | T5-clean-read | T3-pre-screen | T4-self-disable) cacheable="false" ;;
  *) cacheable="true" ;;
esac
if [ "${cache_ttl:-0}" -gt 0 ] && [ -n "$config_hash" ] && [ "$cacheable" = "true" ] \
   && [ "$audit_written" = "true" ] && command -v sha256sum >/dev/null 2>&1 \
   && { [ "$verdict" = "allow" ] || [ "$verdict" = "edit" ] || [ "$verdict" = "deny" ]; }; then
  ckey="$(printf '%s' "${cache_id}|${category}|${config_hash}" | sha256sum | cut -d' ' -f1)"
  if mkdir -p "$cache_dir" 2>/dev/null; then
    jq -cn --arg v "$verdict" --arg r "$revised" --argjson ts "$(date +%s 2>/dev/null || echo 0)" \
      '{verdict:$v,revised:$r,ts:$ts}' > "${cache_dir}/${ckey}.json" 2>/dev/null || true
  fi
fi

if [ "$verdict" = "edit" ]; then
  emit_edit "$revised" "$reason Sága log: ${audit_dir_rel}/${run_id}.json"
fi

# Emit a hook-event for every deny verdict so the substrate is never dark for
# the most consequential deny class. The phase tag distinguishes which deny path
# fired (pre-llm-hard-rule, panel-deny, abstain-fail-closed, injection-deny,
# edit-coerced, critical-concern-veto, audit-write-fail, etc.).
if [ "$verdict" = "deny" ]; then
  _emit_hook_event "thing-orchestrator.sh" "deny" "$tool_name" "${cmd:-${reviewed:-}}" "$phase" 2
fi

emit "$verdict" "$reason Sága log: ${audit_dir_rel}/${run_id}.json"
