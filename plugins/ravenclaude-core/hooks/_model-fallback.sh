#!/usr/bin/env bash
# _model-fallback.sh — SOURCED helper (underscore prefix = sourced like _scrub.sh,
# NOT a registered hook; excluded from the hook count).
#
# Purpose: wrap a RavenClaude `claude -p` call so that when the chosen model is
# UNAVAILABLE / OVERLOADED, the call retries on the next model in a configured
# ladder instead of failing — and FAILS SAFE (the caller's existing abstain exit)
# when the ladder is exhausted. This is the shared mechanism for every RC model
# caller (thing-seat.sh / judge.sh / claude-orchestrate.sh / …) so the retry
# logic lives in ONE place. See knowledge/model-fallback.md for the full design.
#
# SCOPE (load-bearing): this helps RavenClaude's OWN model calls only. It cannot
# rescue the harness safety classifier or the main-loop/session model — RC can't
# fall back the layer it runs inside (see the harness-outage runbook in the
# knowledge file). Net-new vs claude-orchestrate.sh, which falls back to the HOST,
# never to another model.
#
# ── Contract ──────────────────────────────────────────────────────────────────
#   _model_call_with_fallback --runner <fn> [--exclude <csv-of-models>]
#
# The caller provides a one-arg runner function: `<fn> <model>` must run its full
# `claude -p … --model <model> …` invocation, print the model's stdout, write the
# model's stderr to the file named in $_MF_ERRFILE, and return claude's exit code.
# The helper threads each ladder rung through <fn>, classifies failures, and on
# SUCCESS prints the winning model's stdout verbatim (clean — stderr stays in
# $_MF_ERRFILE) and exports _MF_RESOLVED_MODEL (the model that actually answered —
# callers re-check the diversity / anti-self-grade invariants on THIS, not the
# configured model).
#
# Config (env — the caller populates these from comfort-posture.yaml):
#   MODEL_FALLBACK_PRIMARY      the caller's chosen model (ALWAYS tried first; required)
#   MODEL_FALLBACK_ENABLED      1 to enable the ladder; anything else ⇒ primary-only
#                               (DISABLED PATH IS BYTE-IDENTICAL to a single direct call)
#   MODEL_FALLBACK_LADDER       csv of fallback models tried (in order) after primary
#   MODEL_FALLBACK_MAX_RETRIES  max fallback attempts after primary (default 2; hard cap 3)
#
# Exit: 0 with stdout on success; non-zero on exhaustion (caller maps to its
# abstain code). A NON-RETRYABLE failure (auth / bad input / injection) stops
# immediately — retrying another model would only mask the real error + burn budget.
#
# Test seam: the runner is injected, so Gate 120 drives the ladder with a mock
# runner and never calls the real `claude`.

# Guard: this file is meant to be sourced, not executed.
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  echo "_model-fallback.sh is a sourced helper; do not execute it directly." >&2
  exit 64
fi

_MF_DEFAULT_MAX_RETRIES=2
_MF_HARD_CAP=3 # never exceed this many fallback attempts regardless of config

# _mf_classify <error-text> <exit_code> -> echoes one of: retry | skip | stop
#   retry — capacity/connectivity (overloaded/429/529/503/network/timeout): try next rung
#   skip  — this named model is gone (model_not_found/404): skip the rung, try next
#   stop  — auth / bad input / context / pre-call guard: do NOT retry (would mask a real bug)
#   default for an unknown nonzero failure: stop (conservative — never silently mask)
_mf_classify() {
  local txt="$1"
  # Hard stops FIRST (so an "invalid_request" never looks retryable).
  if printf '%s' "$txt" | grep -Eiq 'authentication_error|permission_denied|invalid_api_key|invalid_request_error|context_length_exceeded|prompt is too long'; then
    printf 'stop\n'
    return 0
  fi
  # Named-model-gone: skip this rung only.
  if printf '%s' "$txt" | grep -Eiq 'model_not_found|not_found_error|unknown model|no such model'; then
    printf 'skip\n'
    return 0
  fi
  # Retryable: capacity / connectivity.
  if printf '%s' "$txt" | grep -Eiq 'overloaded_error|rate_limit_error|529|too many requests|service unavailable|\b503\b|could not connect|connection refused|econnrefused|timed out|timeout'; then
    printf 'retry\n'
    return 0
  fi
  # Unknown failure → conservative stop (do not mask an unclassified error).
  printf 'stop\n'
}

# _mf_is_in_csv <needle> <csv>
_mf_is_in_csv() {
  local needle="$1" csv="$2" IFS=','
  local x
  for x in $csv; do
    [ "$x" = "$needle" ] && return 0
  done
  return 1
}

_model_call_with_fallback() {
  local runner="" exclude=""
  while [ $# -gt 0 ]; do
    case "$1" in
      --runner) runner="${2:-}"; shift 2 ;;
      --exclude) exclude="${2:-}"; shift 2 ;;
      *) shift ;;
    esac
  done

  local primary="${MODEL_FALLBACK_PRIMARY:-}"
  if [ -z "$runner" ] || [ -z "$primary" ]; then
    echo "_model_call_with_fallback: --runner and MODEL_FALLBACK_PRIMARY are required" >&2
    return 64
  fi
  if ! declare -F "$runner" >/dev/null 2>&1; then
    echo "_model_call_with_fallback: runner function '$runner' not defined" >&2
    return 64
  fi

  # Build the ordered candidate list: primary FIRST, then the ladder (when enabled),
  # minus excluded models, minus duplicates.
  local -a candidates=("$primary")
  local enabled="${MODEL_FALLBACK_ENABLED:-0}"
  if [ "$enabled" = "1" ]; then
    local IFS=','
    local m
    for m in ${MODEL_FALLBACK_LADDER:-}; do
      [ -z "$m" ] && continue
      _mf_is_in_csv "$m" "$(IFS=,; echo "${candidates[*]}")" && continue
      candidates+=("$m")
    done
  fi

  # max_retries = fallback attempts AFTER the primary; clamp to the hard cap.
  local maxr="${MODEL_FALLBACK_MAX_RETRIES:-$_MF_DEFAULT_MAX_RETRIES}"
  case "$maxr" in
    '' | *[!0-9]*) maxr="$_MF_DEFAULT_MAX_RETRIES" ;; # non-integer ⇒ default (anti-loop)
  esac
  [ "$maxr" -gt "$_MF_HARD_CAP" ] && maxr="$_MF_HARD_CAP"

  # Per-call stderr capture (Phase-1 stderr-capture pattern; never 2>/dev/null,
  # so the error body is classifiable).
  local own_errfile=0
  if [ -z "${_MF_ERRFILE:-}" ]; then
    _MF_ERRFILE="$(mktemp)"
    own_errfile=1
  fi
  export _MF_ERRFILE
  _MF_RESOLVED_MODEL=""
  export _MF_RESOLVED_MODEL

  local attempts=0 idx=0 out rc verdict errtxt model
  local final_rc=1
  for model in "${candidates[@]}"; do
    # Diversity / anti-self-grade: never use an excluded model.
    if [ -n "$exclude" ] && _mf_is_in_csv "$model" "$exclude"; then
      continue
    fi
    # The primary (idx 0) is the first try and does NOT count against max_retries;
    # each subsequent rung is one fallback attempt.
    if [ "$idx" -gt 0 ]; then
      if [ "$attempts" -ge "$maxr" ]; then
        break
      fi
      attempts=$((attempts + 1))
    fi
    idx=$((idx + 1))

    : >"$_MF_ERRFILE"
    out="$("$runner" "$model")"
    rc=$?
    errtxt="$(cat "$_MF_ERRFILE" 2>/dev/null)"
    # The JSON envelope can carry is_error=true with exit 0 — treat that as failure.
    if [ "$rc" -eq 0 ] && ! printf '%s' "$out" | grep -Eq '"is_error"[[:space:]]*:[[:space:]]*true'; then
      _MF_RESOLVED_MODEL="$model"
      export _MF_RESOLVED_MODEL
      # The resolved model must survive command substitution (the caller usually
      # captures stdout in a subshell), so write it to the caller-provided file —
      # callers re-check diversity / anti-self-grade on THIS model.
      [ -n "${_MF_RESOLVED_FILE:-}" ] && printf '%s' "$model" >"$_MF_RESOLVED_FILE"
      printf '%s' "$out"
      [ "$own_errfile" = "1" ] && rm -f "$_MF_ERRFILE" && unset _MF_ERRFILE
      return 0
    fi

    # Classify the failure on the captured stderr + the (error) stdout body.
    verdict="$(_mf_classify "${errtxt}
${out}")"
    final_rc=$rc
    [ "$final_rc" -eq 0 ] && final_rc=1 # is_error-with-exit-0 still a failure
    case "$verdict" in
      stop)
        # Non-retryable: do not try another model — retrying masks the real error.
        printf '%s' "$out"
        [ "$own_errfile" = "1" ] && rm -f "$_MF_ERRFILE" && unset _MF_ERRFILE
        return "$final_rc"
        ;;
      skip)
        # Named model gone: skip this rung WITHOUT spending a retry; try the next.
        [ "$idx" -gt 1 ] && attempts=$((attempts - 1))
        continue
        ;;
      retry)
        continue
        ;;
    esac
  done

  # Ladder exhausted — fail safe (caller maps non-zero to its abstain code).
  printf '%s' "${out:-}"
  [ "$own_errfile" = "1" ] && rm -f "$_MF_ERRFILE" && unset _MF_ERRFILE
  return "$final_rc"
}
