#!/usr/bin/env bash
# claude-orchestrate.sh — Claude-powered team-lead orchestration for non-Claude CLIs.
#
# Used by spawn-team when the `orchestrator:` knob in
# .ravenclaude/comfort-posture.yaml is set to `decide` or `full` AND the host
# is not Claude Code (THING_HOST != claude-code). Under Claude Code the host
# already IS Claude — the knob is a no-op and this script is never called.
#
# Mode `decide`: calls `claude -p --tools ""` with the task brief + agent
#   roster and gets back a structured JSON dispatch plan the host CLI executes.
#   Brain (Claude) / hands (host) split. Lower token cost.
# Mode `full`:   calls `claude -p --tools ""` with the full task and gets back
#   artifact content that the host writes to disk. One bounded call; highest
#   cost; locked intent.
#
# Interface (environment variables + positional arg):
#   $1                        — mode: decide | full (required)
#   RAVENCLAUDE_ORCH_BRIEF    — task description for the nested Claude call (required)
#   RAVENCLAUDE_ORCH_ROSTER   — agent roster JSON (optional; used by decide mode)
#   RAVENCLAUDE_ORCH_SCOPE    — "all" activates the relay-all data-governance guards
#                               (layer C egress floor + optional layer A pseudonymize).
#                               Unset/"team" = team-dispatch path, byte-identical to v0.152.0.
#   THING_MODEL               — model alias/id (default: haiku for decide, sonnet for full)
#
# Exits:
#   0   — success; result JSON or content on stdout
#   7   — recursion guard fired (re-entrant call refused; caller MUST fall back to host)
#   8   — scrub fired (secret-shaped brief detected; never egressses)
#   9   — relay-all egress floor blocked (SCOPE=all + PII may leave a non-in-tenant
#         processor; or the pseudonymizer faulted) — caller MUST fall back to host
#   2   — claude CLI not found (fall back to host)
#   1   — bad args / empty brief
#   3   — claude call failed or returned is_error
#
# FAIL-SAFE: every non-zero exit code means the caller MUST fall back to host
# orchestration (the `off` path). This script never hard-blocks.
#
# Copying the `claude -p` invocation pattern from thing-seat.sh:
#   - plain `claude -p` (never `--bare` — SUBSCRIPTION/OAuth compatible)
#   - mktemp scratch dir so the consumer's project CLAUDE.md is NOT loaded
#   - sources hooks/_scrub.sh for the egress secret backstop
#   - defangs ${CLAUDE_PROJECT_DIR}
#   - wraps the brief in the canonical <untrusted-NONCE> envelope

set -euo pipefail

# ── ARG VALIDATION ─────────────────────────────────────────────────────────────
mode="${1:-}"
if [ -z "$mode" ]; then
  echo "claude-orchestrate.sh: mode required (decide|full)" >&2; exit 1
fi
case "$mode" in
  decide|full) ;;
  *)
    echo "claude-orchestrate.sh: unknown mode '$mode' — must be decide or full" >&2; exit 1
    ;;
esac

# ── RECURSION GUARD — layer 1: RAVENCLAUDE_ORCH_ACTIVE ─────────────────────────
# This script sets RAVENCLAUDE_ORCH_ACTIVE=1 before calling claude. If a
# nested call ever reaches here with the flag already set, that is a re-entrant
# orchestration loop — refuse it immediately.
# One-liner for deterministic gate stripping (Gate 102 teeth test strips this line).
[ "${RAVENCLAUDE_ORCH_ACTIVE:-0}" = "1" ] && { echo "orchestrate: RAVENCLAUDE_ORCH_ACTIVE guard fired — re-entrant call refused" >&2; exit 7; }

# ── RECURSION GUARD — layer 2: THING_SEAT_ACTIVE ───────────────────────────────
# The tribunal sets THING_SEAT_ACTIVE=1. Spawning an orchestrator inside a
# tribunal seat is deeper, unexpected recursion — refuse it.
[ "${THING_SEAT_ACTIVE:-0}" = "1" ] && { echo "orchestrate: THING_SEAT_ACTIVE guard fired — refused inside tribunal seat" >&2; exit 7; }

brief="${RAVENCLAUDE_ORCH_BRIEF:-}"
roster="${RAVENCLAUDE_ORCH_ROSTER:-}"
if [ -z "$brief" ]; then
  echo "claude-orchestrate.sh: RAVENCLAUDE_ORCH_BRIEF is empty — nothing to orchestrate" >&2; exit 1
fi

# ── RELAY-ALL DATA GOVERNANCE — layer C floor (+ layer A flag) ──────────────────
# Active ONLY when the host's relay-mode directive invokes us with SCOPE=all (the
# every-prompt relay). Team-dispatch orchestration (SCOPE unset/"team") skips this
# whole block and is byte-identical to v0.152.0. Full rationale + the cited
# provider facts: plugins/ravenclaude-core/knowledge/orchestrator-data-egress.md
_orch_posture_flag() {
  # Read a top-level flat key from the consumer's comfort-posture.yaml. Prints the
  # lowercased value (comments/whitespace stripped) or empty. Fail-safe: no file -> "".
  local f="${CLAUDE_PROJECT_DIR:-.}/.ravenclaude/comfort-posture.yaml"
  [ -f "$f" ] || return 0
  # `grep || true` keeps a key-miss (grep exit 1) from aborting under `set -e`.
  { grep -E "^$1:" "$f" 2>/dev/null || true; } | head -1 \
    | sed -E "s/^$1:[[:space:]]*//; s/[[:space:]]*(#.*)?$//" \
    | tr '[:upper:]' '[:lower:]'
  return 0
}

if [ "${RAVENCLAUDE_ORCH_SCOPE:-}" = "all" ]; then
  # Source the event substrate (fail-safe: defines _emit_hook_event or we stub it).
  _ev_helper="$(dirname "$0")/../hooks/_emit-event.sh"
  # shellcheck source=/dev/null
  [ -f "$_ev_helper" ] && . "$_ev_helper" 2>/dev/null || true
  if ! command -v _emit_hook_event >/dev/null 2>&1; then
    _emit_hook_event() { :; }
  fi

  # Layer C — deterministic egress floor. Permit egress only when the destination
  # is in-tenant (Bedrock/Vertex), ZDR is attested, or the repo is flagged no-PII.
  # Default (none of these) = assume PII + out-of-tenant -> fail closed.
  _egress_ok=0
  case "${CLAUDE_CODE_USE_BEDROCK:-}" in 1 | true | yes | TRUE | True) _egress_ok=1 ;; esac
  case "${CLAUDE_CODE_USE_VERTEX:-}" in 1 | true | yes | TRUE | True) _egress_ok=1 ;; esac
  case "$(_orch_posture_flag orchestrator_zdr_confirmed)" in true | yes | 1) _egress_ok=1 ;; esac
  case "$(_orch_posture_flag orchestrator_repo_pii)" in false | no | 0) _egress_ok=1 ;; esac
  if [ "$_egress_ok" -ne 1 ]; then
    _emit_hook_event "claude-orchestrate.sh" "deny" "Orchestrate" "relay-all" "egress-floor-blocked" 9 2>/dev/null || true
    echo "claude-orchestrate.sh: relay-all egress floor — destination not proven in-tenant/ZDR and the repo may hold PII; refusing to egress. Falling back to host-direct." >&2
    echo "  Enable by ANY of: run Claude on Bedrock/Vertex (your cloud), OR set orchestrator_zdr_confirmed: true (ZDR on for your Anthropic org), OR orchestrator_repo_pii: false." >&2
    exit 9
  fi
  _orch_pseudo="$(_orch_posture_flag orchestrator_pseudonymize)"
fi

# ── SECRET SCRUB — egress backstop ─────────────────────────────────────────────
# Source the shared scrub helper (mirrors thing-seat.sh §B.9.4).
# Run on the FULL brief+roster before any part reaches the model API.
_scrub_helper="$(dirname "$0")/../hooks/_scrub.sh"
# shellcheck source=/dev/null
[ -f "$_scrub_helper" ] && . "$_scrub_helper" 2>/dev/null || true

# Inline fallback: if _scrub.sh was not sourced, define the patterns locally.
if ! declare -p _secret_patterns >/dev/null 2>&1; then
  _secret_patterns=(
    'AKIA[0-9A-Z]{12,}'
    'sk-(ant-)?[A-Za-z0-9-]{20,}'
    'sk_live_[A-Za-z0-9]{24,}'
    'ghp_[A-Za-z0-9]{30,}'
    'github_pat_[A-Za-z0-9_]{20,}'
    'glpat-[A-Za-z0-9_-]{15,}'
    'xox[baprs]-[A-Za-z0-9-]{10,}'
    'AIza[0-9A-Za-z_-]{30,}'
    'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{20,}'
    '-----BEGIN [A-Z ]*PRIVATE KEY-----'
    '--password[=[:space:]][^[:space:]]+'
    '--token[=[:space:]][^[:space:]]+'
  )
fi

_scan="${brief} ${roster}"
for _p in "${_secret_patterns[@]}"; do
  if printf '%s' "$_scan" | grep -Eiq -e "$_p"; then
    echo "claude-orchestrate.sh: secret-shaped material in brief/roster — refusing egress; fall back to host" >&2
    exit 8
  fi
done

# ── AVAILABILITY CHECK ─────────────────────────────────────────────────────────
# A cheap, deterministic preflight. If claude is absent, fall back immediately.
command -v claude >/dev/null 2>&1 || {
  echo "claude-orchestrate.sh: claude CLI not found in PATH — fall back to host" >&2
  exit 2
}

# ── SCRATCH DIR + DEFANG CLAUDE_PROJECT_DIR ────────────────────────────────────
# Run from a throwaway dir so the consumer's project CLAUDE.md is NOT
# auto-discovered into the nested session (same pattern as thing-seat.sh).
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

# ── LAYER A — pseudonymize structured PII before egress (relay-all, opt-in) ──────
# Replace email/SSN/card/phone shapes in the brief with opaque tokens, keeping the
# token->value map ONLY in the trap-cleaned scratch dir (it never egresses). The
# returned content is de-tokenized below before the host writes it. Fail closed: a
# pseudonymizer fault exits 9 (caller falls back) rather than egress un-tokenized PII.
_pseudo_active=0
if [ "${RAVENCLAUDE_ORCH_SCOPE:-}" = "all" ]; then
  case "${_orch_pseudo:-}" in
    true | yes | 1)
      _pz="$(dirname "$0")/pseudonymize-brief.py"
      _pii_map="$scratch/pii-map.json"
      _pii_map_roster="$scratch/pii-map-roster.json"
      if [ -f "$_pz" ] && command -v python3 >/dev/null 2>&1; then
        if _enc_brief="$(printf '%s' "$brief" | python3 "$_pz" encode --map-file "$_pii_map" 2>/dev/null)"; then
          brief="$_enc_brief"
          _pseudo_active=1
        else
          echo "claude-orchestrate.sh: PII pseudonymizer failed — refusing to egress un-tokenized brief (fail closed). Fall back to host." >&2
          exit 9
        fi
        # Tokenize the roster too (decide mode) so PII there is not the one raw leak.
        if [ -n "$roster" ]; then
          if _enc_roster="$(printf '%s' "$roster" | python3 "$_pz" encode --map-file "$_pii_map_roster" 2>/dev/null)"; then
            roster="$_enc_roster"
          else
            echo "claude-orchestrate.sh: PII pseudonymizer failed on roster — fail closed. Fall back to host." >&2
            exit 9
          fi
        fi
      else
        # A was requested but is unavailable — make the downgrade VISIBLE (never silent).
        # Layer C (the egress floor) has already permitted egress, so this is not a leak
        # past the floor; it is a defense-in-depth layer that couldn't run.
        echo "claude-orchestrate.sh: orchestrator_pseudonymize requested but python3 or pseudonymize-brief.py is unavailable — egressing un-tokenized (the layer-C egress floor still governs). Install python3 to enable layer A." >&2
      fi
      ;;
  esac
fi

# Strip control characters + bound length, identical to thing-seat.sh §3b.
safe_project_dir="$(printf '%s' "${CLAUDE_PROJECT_DIR:-unknown}" | tr -d '\000-\037' | tr -c '[:print:]' '_' | cut -c1-512)"
[ -z "$safe_project_dir" ] && safe_project_dir="unknown"

# Per-call nonce against delimiter injection (same as thing-seat.sh §B.9.2).
nonce="$(head -c 16 /dev/urandom 2>/dev/null | od -An -tx1 | tr -d ' \n')"
[ -z "$nonce" ] && nonce="$(printf '%04x%04x%04x%04x' "$RANDOM" "$RANDOM" "$RANDOM" "$RANDOM")"

# Defang any literal <untrusted…> boundary tags in the brief and roster.
safe_brief="$(printf '%s' "$brief" | sed 's#<\(/\{0,1\}\)untrusted#<\1u-ntrusted#g')"
safe_roster=""
[ -n "$roster" ] && safe_roster="$(printf '%s' "$roster" | sed 's#<\(/\{0,1\}\)untrusted#<\1u-ntrusted#g')"

# ── BUILD PROMPTS ──────────────────────────────────────────────────────────────
if [ "$mode" = "decide" ]; then
  # decide: return a JSON dispatch plan the host executes.
  # --tools "" is the non-negotiable structural recursion guard (layer 3):
  # the nested session has ZERO tools, so a prompt-injected session cannot
  # call spawn-team, read files, or invoke hooks regardless of env vars.
  model="${THING_MODEL:-claude-haiku-4-5-20251001}"
  system_prompt="You are the RavenClaude Team Lead orchestration planner. Read the task brief and agent roster and return ONLY a structured JSON dispatch plan — no prose, no markdown fences.

Plan shape: {\"agents\":[{\"role\":\"<role>\",\"brief\":\"<brief>\",\"depends_on\":[]},...],\"parallelism\":\"sequential|parallel\",\"reasoning\":\"<= 200 chars\"}

Rules:
- depends_on: list of role names this agent waits for (empty = run immediately).
- Keep agent briefs concise and action-oriented.
- You have NO tools — reason only.
- Project root: ${safe_project_dir}"

  user_prompt="Task brief:
<untrusted-${nonce}>
${safe_brief}
</untrusted-${nonce}>

Agent roster:
<untrusted-${nonce}>
${safe_roster:-<none provided>}
</untrusted-${nonce}>

Return the JSON dispatch plan only."

else
  # full: reason through the whole task and return artifact content.
  # Still uses --tools "" to bound the blast radius (no tool calls from the
  # nested session, regardless of injection). Bounded cost; the host writes.
  model="${THING_MODEL:-claude-sonnet-5}"
  system_prompt="You are the RavenClaude Team Lead. Reason through the full task in the brief and return the artifact content directly — code, markdown, JSON, or whatever the task produces. The host handles all file writes.

Rules:
- Return artifact content only (no wrapping meta-commentary before the artifact).
- You have NO tools — reason from the brief alone.
- Project root: ${safe_project_dir}"

  user_prompt="Task brief:
<untrusted-${nonce}>
${safe_brief}
</untrusted-${nonce}>

Produce the artifact content now."
fi

# ── MARK ACTIVE + CALL CLAUDE ─────────────────────────────────────────────────
# Export RAVENCLAUDE_ORCH_ACTIVE=1 into the nested run so ANY re-entrant call
# to this script is refused at entry (layer 1 of the recursion guard above).
export RAVENCLAUDE_ORCH_ACTIVE=1

printf '[claude-orchestrate] mode=%s host=%s model=%s\n' "$mode" "${THING_HOST:-unknown}" "$model" >&2

# Layer 3 (structural): --tools "" prevents tool calls from the nested session,
# regardless of prompt injection, independently of the env-var layers above.
#
# Model-fallback (opt-in, P2): on an OVERLOADED/unavailable model the same call
# retries on the next ladder rung BEFORE falling back to the host; an auth/bad-input
# error never retries (would mask a real bug). Config comes from comfort-posture.yaml;
# default OFF ⇒ a single call, byte-identical to the prior behavior. The runner keeps
# the scratch cwd + defanged CLAUDE_PROJECT_DIR + --tools "" exactly as before.
_mf_helper="$(dirname "$0")/../hooks/_model-fallback.sh"
# shellcheck source=/dev/null
[ -f "$_mf_helper" ] && . "$_mf_helper" 2>/dev/null || true

_orch_claude_run() {
  cd "$scratch" && CLAUDE_PROJECT_DIR="$safe_project_dir" \
    claude -p \
    --output-format json \
    --model "$1" \
    --tools "" \
    --append-system-prompt "$system_prompt" \
    "$user_prompt" 2>"${_MF_ERRFILE:-/dev/null}"
}

if declare -F _model_call_with_fallback >/dev/null 2>&1; then
  _mf_load_config
  MODEL_FALLBACK_PRIMARY="$model"
  export MODEL_FALLBACK_PRIMARY MODEL_FALLBACK_ENABLED MODEL_FALLBACK_LADDER MODEL_FALLBACK_MAX_RETRIES
  raw="$(_model_call_with_fallback --runner _orch_claude_run)" || {
    echo "claude-orchestrate.sh: claude invocation failed — fall back to host" >&2
    exit 3
  }
else
  # Helper absent — preserve the exact prior single-call behavior.
  raw="$(_orch_claude_run "$model" 2>/dev/null)" || {
    echo "claude-orchestrate.sh: claude invocation failed — fall back to host" >&2
    exit 3
  }
fi

# A non-zero is_error in the envelope (e.g. auth failure) still exits 0 from
# claude — check it explicitly (the helper also treats is_error as failure; this
# guards the no-helper branch and a single-rung success).
if [ "$(printf '%s' "$raw" | jq -r '.is_error // false' 2>/dev/null)" = "true" ]; then
  echo "claude-orchestrate.sh: claude returned is_error — fall back to host" >&2
  exit 3
fi

result="$(printf '%s' "$raw" | jq -r '.result // empty' 2>/dev/null || true)"
[ -z "$result" ] && result="$raw"

# Layer A — restore pseudonymized PII in the returned content before the host
# writes it (the map lives only in the scratch dir; decode is best-effort).
if [ "${_pseudo_active:-0}" = "1" ]; then
  result="$(printf '%s' "$result" | python3 "$_pz" decode --map-file "$_pii_map" 2>/dev/null || printf '%s' "$result")"
  [ -f "${_pii_map_roster:-}" ] && result="$(printf '%s' "$result" | python3 "$_pz" decode --map-file "$_pii_map_roster" 2>/dev/null || printf '%s' "$result")"
fi

printf '%s\n' "$result"
