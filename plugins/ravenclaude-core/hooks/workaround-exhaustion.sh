#!/usr/bin/env bash
# workaround-exhaustion.sh — the blocked-exhaustion gate.
#
# WHY (2026-09-17 incident, this repo). After one guard denied one route, the
# agent CONSIDERED the alternatives, called each blocked at its first plausible
# objection, handed the user a menu of manual steps — twice — and then re-armed
# eight silent check-ins on a blocker it had declared itself. The two routes
# that worked (an API write, a CI-runner dispatch) were available the whole
# time and took minutes once someone said "find a way". "Considered" felt like
# "tried" from the inside, and the exhaustion claim was never written down, so
# it was never falsifiable. Prose ("keep trying") has no gate on that decision,
# and it degrades fastest on a weaker model.
#
# WHAT. Make the stop decision MECHANICAL. After any RavenClaude guard deny in
# this session, the two surfaces where giving up becomes an ACTION — asking the
# human how to proceed (PreToolUse AskUserQuestion) and ending the turn on a
# hand-back (Stop) — require a ledger of EXECUTED, distinct-channel attempts:
#
#   .ravenclaude/runs/<session>/workaround-ledger.jsonl        one row per route
#   {"ts","channel","tried":"yes|no","result","bypass_test"}
#
# A row counts toward the floor (default 3) only with tried=yes AND a non-empty
# result — the verbatim error or success. `tried: no` is a legal row: it is how
# "I considered it" gets written down honestly, and it does not count.
# `bypass_test` names the REVIEWABLE ARTIFACT the route produces (a commit on a
# PR, a CI run log). That is the discriminator this repo was missing: a
# legitimate route changes WHO CAN REVIEW the effect; a bypass produces the same
# effect while hiding it from the guard (encoding, aliasing, path-splitting,
# sleep substitutes). Written down, a weaker model can apply it; unwritten, a
# vibe decides, and the vibe defaults to stopping.
#
# Escape: `rc workaround blocked-ok "<reason>"` — logged as a warn event, never
# silent. The route catalog (knowledge/workaround-routes.md) lists the alternate
# channels per blocked-action class in cost order, gotchas already paid for, so
# the model reads the next route off a list instead of having to invent it.
#
# KNOBS (.ravenclaude/comfort-posture.yaml; ABSENT ⇒ off — fully inert):
#   workaround_exhaustion: off | warn | block
#   workaround_exhaustion_floor: 3           distinct executed channels required
#   workaround_exhaustion_max_blocks: 4      consecutive Stop blocks, then force-allow
#
# HONEST LIMITS. No hook sees the model DECIDING to give up in chat; this gate
# covers the two surfaces where giving up becomes an action, which is where all
# of the incident's damage happened. The Stop lane needs the host's
# `last_assistant_message` (Claude Code carries it); on a host without it the
# Stop lane is silent by construction. Rows are agent-written: nothing here
# proves a row's `result` came from a real call — a per-tool channel log that
# would cross-check it is a named follow-up, not a claim.
#
# DELIVERY. warn → additionalContext via _advise.sh (stderr at exit 0 is
# MEASURED undelivered to the model); block → PreToolUse permissionDecision
# deny, or Stop decision:block bounded by max_blocks so it cannot deadlock.
# Every verdict is emitted to hook-events.jsonl as DERIVED VALUES ONLY (counts,
# channel-enum members, sanitized tokens) — never a ledger row's free text.
#
# Portable: bash 3.2 — no declare -A / mapfile / ${x^^} / globstar; no GNU
# timeout / grep -P / sed -i; regex word boundaries spelled without `\b`.
# jq is required (absent ⇒ fail-safe no-op).
#
# Usage:
#   workaround-exhaustion.sh ask          PreToolUse(AskUserQuestion), payload on stdin
#   workaround-exhaustion.sh stop         Stop, payload on stdin
#   workaround-exhaustion.sh tried  [--session S] --channel C [--tried yes|no] --result R --bypass-test B
#   workaround-exhaustion.sh blocked-ok [--session S] <reason>
#   workaround-exhaustion.sh status [--session S]
#   workaround-exhaustion.sh list   [--session S]

set -uo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd)" || here="."
sub="${1:-}"
[ $# -gt 0 ] && shift

CHANNELS="local-edit local-bash mcp-api ci-runner other-session human"
HOOKNAME="workaround-exhaustion.sh"
payload=""

_is_channel() {
  local c
  for c in $CHANNELS; do [ "$c" = "${1:-}" ] && return 0; done
  return 1
}
_token() { printf '%s' "${1:-}" | tr -dc 'A-Za-z0-9._:/-' | cut -c1-64; }
_now() { date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || printf '1970-01-01T00:00:00Z'; }

# Project root: explicit env, else the payload's cwd, else the working dir.
_root() {
  if [ -n "${CLAUDE_PROJECT_DIR:-}" ]; then printf '%s' "$CLAUDE_PROJECT_DIR"; return 0; fi
  local c=""
  if [ -n "$payload" ] && command -v jq >/dev/null 2>&1; then
    c="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null || true)"
  fi
  printf '%s' "${c:-$PWD}"
}

# Session id: explicit arg, else $CLAUDE_SESSION_ID, else the payload's
# .session_id, else the run dir whose hook-events.jsonl is newest (CLI fallback
# only — the nudge prints `--session <id>` verbatim so the agent never guesses).
_session() {
  local s="${1:-}"
  [ -z "$s" ] && s="${CLAUDE_SESSION_ID:-}"
  if [ -z "$s" ] && [ -n "$payload" ]; then
    s="$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null || true)"
  fi
  if [ -z "$s" ] && [ -d "$root/.ravenclaude/runs" ]; then
    s="$(ls -t "$root"/.ravenclaude/runs/*/hook-events.jsonl 2>/dev/null | head -1 | awk -F/ '{print $(NF-1)}')"
  fi
  s="$(printf '%s' "$s" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
  case "$s" in .|..|"") s="unknown" ;; esac
  printf '%s' "$s"
}

# Minimal scalar read — the idiom worktree-guard.sh uses; no PyYAML.
_knob() { # $1=key $2=default
  local v=""
  if [ -f "${posture:-/nonexistent}" ]; then
    v="$(sed -n "s/^[[:space:]]*$1:[[:space:]]*\([A-Za-z0-9]\{1,\}\).*/\1/p" "$posture" 2>/dev/null | head -1)"
  fi
  printf '%s' "${v:-$2}"
}

# The most recent guard deny this session NOT emitted by this gate (our own
# block must never re-anchor the window it measures). Prints
# "ts<TAB>hook<TAB>rule"; returns 1 when there is none.
_last_deny() {
  [ -f "${events:-/nonexistent}" ] || return 1
  local line
  line="$(jq -r -R 'fromjson? // empty | select(.verdict=="deny" and (.hook // "") != "workaround-exhaustion.sh") | [(.ts // ""), (.hook // ""), (.rule // "")] | @tsv' "$events" 2>/dev/null | tail -1)"
  [ -n "$line" ] || return 1
  printf '%s' "$line"
}

# Distinct EXECUTED channels since the deny: tried=yes, a non-empty result, and
# a channel in the enum (anything else is ignored and never echoed).
_executed_channels() { # $1=deny_ts
  [ -f "${ledger:-/nonexistent}" ] || return 0
  jq -r -R --arg d "$1" 'fromjson? // empty | select((.ts // "") >= $d) | select((.tried // "") == "yes") | select(((.result // "") | tostring | length) > 0) | (.channel // "")' "$ledger" 2>/dev/null \
    | while IFS= read -r c; do _is_channel "$c" && printf '%s\n' "$c"; done | sort -u
}

_blocked_ok_since() { # $1=deny_ts -> the escape reason logged since the deny, if any
  [ -f "${ledger:-/nonexistent}" ] || return 0
  jq -r -R --arg d "$1" 'fromjson? // empty | select((.ts // "") >= $d) | select(((.blocked_ok // "") | tostring | length) > 0) | .blocked_ok' "$ledger" 2>/dev/null | tail -1
}

_emit() { # $1=verdict $2=tool $3=rule — derived values only
  if [ -f "$here/_emit-event.sh" ]; then
    # shellcheck source=/dev/null
    . "$here/_emit-event.sh" 2>/dev/null || true
    if command -v _emit_hook_event >/dev/null 2>&1; then
      CLAUDE_PROJECT_DIR="$root" CLAUDE_SESSION_ID="$sid" _emit_hook_event "$HOOKNAME" "$1" "$2" "" "$3" 0 || true
    fi
  fi
}

_rc_path() { printf '%s' "$(cd "$here/.." 2>/dev/null && pwd)/bin/rc"; }

_untried() { # $1=newline list of tried channels -> space-separated rest
  local c out=""
  for c in $CHANNELS; do
    printf '%s\n' "$1" | grep -qx "$c" 2>/dev/null || out="$out $c"
  done
  printf '%s' "${out# }"
}

_message() { # $1=surface $2=n $3=floor $4=tried(space list) $5=untried $6=deny_ts $7=deny_hook $8=deny_rule $9=mode ${10}=suffix
  local rc; rc="$(_rc_path)"
  local tried_txt="${4:-}"
  [ -z "$tried_txt" ] && tried_txt="none"
  cat <<EOF
[workaround-exhaustion] A RavenClaude guard denied a tool call this session (last deny: $6, hook $7, rule $8) and this $1 reads as a hand-back — but the workaround ledger shows $2 of $3 executed, distinct-channel attempts since that deny (executed: $tried_txt).

Untried channels: ${5:-none}. The route catalog lists the alternate channels for each blocked-action class in cost order, gotchas already paid for — read it before deciding a goal is blocked:
  knowledge/workaround-routes.md (under this plugin's root)

Record each REAL attempt — executed, not considered — with its verbatim result:
  bash $rc workaround tried --session $sid --channel <channel> --result "<verbatim error or success>" --bypass-test "<the reviewable artifact this route produces>"
A row counts only with tried=yes AND a non-empty result. A route that hides the effect from the guard (encoding, aliasing, splitting a path across variables, a sleep substitute) is a bypass, not a channel — do not record it, do not take it.

If this genuinely is a hand-back, say why and log it (logged as a warn event, never silent):
  bash $rc workaround blocked-ok --session $sid "<the specific route/permission you lack>"
(mode: $9${10})
EOF
}

_status_text() {
  local d="" dts="" dh="" dr="" tried="" n=0 floor esc
  floor="$(_knob workaround_exhaustion_floor 3)"
  case "$floor" in (*[!0-9]*|"") floor=3 ;; esac
  if d="$(_last_deny)"; then
    dts="$(printf '%s' "$d" | cut -f1)"; dh="$(_token "$(printf '%s' "$d" | cut -f2)")"; dr="$(_token "$(printf '%s' "$d" | cut -f3)")"
    tried="$(_executed_channels "$dts")"
    n="$(printf '%s' "$tried" | grep -c . 2>/dev/null || true)"; n="${n:-0}"
    printf 'session: %s\nlast deny: %s (hook %s, rule %s)\nexecuted distinct channels since: %s of %s [%s]\nuntried: %s\n' \
      "$sid" "$dts" "${dh:-?}" "${dr:-?}" "$n" "$floor" "$(printf '%s' "$tried" | tr '\n' ' ' | sed 's/ $//')" "$(_untried "$tried")"
    esc="$(_blocked_ok_since "$dts")"
    [ -n "$esc" ] && printf 'blocked-ok logged since the deny: yes\n'
  else
    printf 'session: %s\nlast deny: none this session — the gate is inert\n' "$sid"
  fi
  printf 'ledger: %s\n' "$ledger"
}

# ── Shapes (POSIX ERE, matched under nocasematch; no `\b`) ──────────────────
# A question is a hand-back when it carries blocked/permission/alternative
# vocabulary — tied to that vocabulary, not to every "do you want me to": the
# deny precondition keeps this narrow, and the blocked-ok escape is one line.
ASK_SHAPE='(blocked|can.?.?.?t([^[:alnum:]]|$)|unable to|not possible|no way (to|around)|manually|by hand|hand(ing)? (this |it )?back|which (option|route|approach|path)|how (should|do you want me to|would you like me to) proceed|remaining option|denied|permission|work.?around|alternative|escalat)'
# A turn end is a hand-back when the final message tells the human to act or
# declares the goal unreachable from here. Bare "manually" is NOT in this list
# ("I verified it manually" is ordinary prose); the hand-back verbs are.
STOP_SHAPE='(i.?.?.?m blocked|i am blocked|blocked on|can.?.?.?t (do|proceed|apply|push|complete|make|get|run|fix)|cannot (do|proceed|apply|push|complete|make|get|run|fix)|no way (to|around)|not possible (from|in|within) this session|you.?.?.?ll need to|you (will )?need to|you (would |will )?have to|(run|apply|check|paste|merge|set|push) (it|this|that|them)? ?manually|manually (run|apply|check|paste|merge|set|push)|by hand|hand(ing)? (this |it )?back|remaining option|please (run|apply|paste|do|merge)|don.?.?.?t have (a way|access|the means|the ability)|genuine (tool|access) gap|out of (options|routes))'

# ── Hook lanes ───────────────────────────────────────────────────────────────
_gate() { # $1=ask|stop
  trap 'exit 0' EXIT                       # hook lanes are fail-safe: allow on any error
  payload="$(cat 2>/dev/null || true)"
  command -v jq >/dev/null 2>&1 || exit 0
  root="$(_root)"
  posture="$root/.ravenclaude/comfort-posture.yaml"
  [ -f "$posture" ] || exit 0              # opt-in by posture presence
  local mode; mode="$(_knob workaround_exhaustion off)"
  case "$mode" in warn|block) ;; *) exit 0 ;; esac
  local floor maxb
  floor="$(_knob workaround_exhaustion_floor 3)";        case "$floor" in (*[!0-9]*|"") floor=3 ;; esac
  maxb="$(_knob workaround_exhaustion_max_blocks 4)";    case "$maxb"  in (*[!0-9]*|"") maxb=4  ;; esac
  sid="$(_session)"
  run="$root/.ravenclaude/runs/$sid"
  events="$run/hook-events.jsonl"
  ledger="$run/workaround-ledger.jsonl"
  local bf="$run/workaround-exhaustion.blocks"

  local d
  d="$(_last_deny)" || { [ -f "$bf" ] && rm -f "$bf" 2>/dev/null; exit 0; }
  local dts dh dr
  dts="$(printf '%s' "$d" | cut -f1)"; dh="$(_token "$(printf '%s' "$d" | cut -f2)")"; dr="$(_token "$(printf '%s' "$d" | cut -f3)")"
  [ -n "$dts" ] || exit 0

  local text="" surface="" tool="" shape=""
  if [ "$1" = "ask" ]; then
    text="$(printf '%s' "$payload" | jq -r '([.tool_input.questions[]?.question // empty] + [.tool_input.questions[]?.options[]?.label // empty] + [.tool_input.question // empty]) | join(" ")' 2>/dev/null || true)"
    surface="question"; tool="AskUserQuestion"; shape="$ASK_SHAPE"
  else
    text="$(printf '%s' "$payload" | jq -r '.last_assistant_message // .lastAssistantMessage // empty' 2>/dev/null || true)"
    [ -n "$text" ] || exit 0               # host without the field: the Stop lane is silent by construction
    surface="turn end"; tool="Stop"; shape="$STOP_SHAPE"
  fi
  shopt -s nocasematch
  if ! [[ "$text" =~ $shape ]]; then shopt -u nocasematch; [ -f "$bf" ] && rm -f "$bf" 2>/dev/null; exit 0; fi
  shopt -u nocasematch

  # Escape: a blocked-ok row since the deny releases the gate — and is logged.
  if [ -n "$(_blocked_ok_since "$dts")" ]; then
    _emit warn "$tool" "workaround-blocked-ok"
    [ -f "$bf" ] && rm -f "$bf" 2>/dev/null
    exit 0
  fi

  local tried n
  tried="$(_executed_channels "$dts")"
  n="$(printf '%s' "$tried" | grep -c . 2>/dev/null || true)"; n="${n:-0}"
  if [ "$n" -ge "$floor" ]; then [ -f "$bf" ] && rm -f "$bf" 2>/dev/null; exit 0; fi

  local suffix="" blocks=0
  if [ "$mode" = "block" ] && [ "$1" = "stop" ]; then
    [ -f "$bf" ] && blocks="$(cat "$bf" 2>/dev/null || echo 0)"
    case "$blocks" in (*[!0-9]*|"") blocks=0 ;; esac
    blocks=$((blocks + 1))
    if [ "$blocks" -ge "$maxb" ]; then
      rm -f "$bf" 2>/dev/null || true
      _emit warn "$tool" "workaround-force-allow:$blocks/$maxb"
      printf '%s\n' "[workaround-exhaustion] floor still unmet after $blocks blocked stops; releasing the Stop gate so the session can end. The ledger shows $n of $floor executed channels — this work is NOT proven exhausted." >&2
      exit 0
    fi
    printf '%s' "$blocks" > "$bf" 2>/dev/null || true
    suffix="; stop blocked $blocks/$maxb"
  fi

  local msg
  msg="$(_message "$surface" "$n" "$floor" "$(printf '%s' "$tried" | tr '\n' ' ' | sed 's/ $//')" "$(_untried "$tried")" "$dts" "${dh:-?}" "${dr:-?}" "$mode" "$suffix")"

  if [ "$mode" = "block" ]; then
    _emit deny "$tool" "workaround-floor-unmet:$n/$floor"
    if [ "$1" = "ask" ]; then
      jq -cn --arg r "$msg" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
    else
      jq -cn --arg r "$msg" '{hookSpecificOutput:{hookEventName:"Stop",additionalContext:$r},decision:"block",reason:$r}'
    fi
    exit 0
  fi

  # warn: deliver as additionalContext — the one advisory channel the model sees.
  _emit warn "$tool" "workaround-floor-unmet:$n/$floor"
  if [ -f "$here/_advise.sh" ]; then
    # shellcheck source=/dev/null
    . "$here/_advise.sh"
    if [ "$1" = "ask" ]; then rc_advise_init PreToolUse 0; else rc_advise_init Stop 0; fi
  fi
  printf '%s\n' "$msg" >&2
  exit 0
}

# ── CLI lanes (used by `rc workaround …`; no payload; loud on bad input) ─────
_cli_init() { # $1=session or empty — sets the globals the lanes read
  root="$(_root)"
  posture="$root/.ravenclaude/comfort-posture.yaml"
  sid="$(_session "${1:-}")"
  run="$root/.ravenclaude/runs/$sid"
  events="$run/hook-events.jsonl"
  ledger="$run/workaround-ledger.jsonl"
}

_scrub() { # secret-shaped tokens never reach the ledger (fail-safe passthrough)
  if [ -f "$here/_scrub.sh" ]; then
    # shellcheck source=/dev/null
    . "$here/_scrub.sh" 2>/dev/null || true
  fi
  if command -v _scrub_reason >/dev/null 2>&1; then _scrub_reason "${1:-}"; else printf '%s' "${1:-}"; fi
}

_need_jq() { command -v jq >/dev/null 2>&1 || { echo "workaround-exhaustion: jq is required" >&2; exit 2; }; }

case "$sub" in
  ask|stop)
    _gate "$sub"
    ;;
  tried)
    _need_jq
    ch="" tr="yes" res="" bt="" s=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --session)     s="${2:-}"; shift; [ $# -gt 0 ] && shift ;;
        --channel)     ch="${2:-}"; shift; [ $# -gt 0 ] && shift ;;
        --tried)       tr="${2:-}"; shift; [ $# -gt 0 ] && shift ;;
        --result)      res="${2:-}"; shift; [ $# -gt 0 ] && shift ;;
        --bypass-test) bt="${2:-}"; shift; [ $# -gt 0 ] && shift ;;
        *) echo "workaround-exhaustion tried: unknown argument '$1'" >&2; exit 2 ;;
      esac
    done
    _cli_init "$s"
    if ! _is_channel "$ch"; then
      echo "workaround-exhaustion tried: --channel must be one of: $CHANNELS" >&2; exit 2
    fi
    case "$tr" in yes|no) ;; *) echo "workaround-exhaustion tried: --tried must be yes|no" >&2; exit 2 ;; esac
    if [ "$tr" = "yes" ] && [ -z "$res" ]; then
      echo "workaround-exhaustion tried: a tried=yes row needs --result — the verbatim error or success. 'Considered' is not a result; record it as --tried no." >&2; exit 2
    fi
    if [ -z "$bt" ]; then
      echo "workaround-exhaustion tried: --bypass-test is required — what REVIEWABLE artifact does this route produce (a PR commit, a CI run log)? If the honest answer is 'none, it hides the effect from the guard', that is a bypass, not a channel: do not record it." >&2; exit 2
    fi
    res="$(_scrub "$res")"; bt="$(_scrub "$bt")"
    mkdir -p "$run" 2>/dev/null || { echo "workaround-exhaustion: cannot create $run" >&2; exit 2; }
    jq -cn --arg ts "$(_now)" --arg c "$ch" --arg t "$tr" --arg r "$res" --arg b "$bt" \
      '{schema_version:1, ts:$ts, channel:$c, tried:$t, result:$r, bypass_test:$b, actor:"agent"}' >> "$ledger" || exit 2
    echo "recorded: channel=$ch tried=$tr"
    _status_text
    ;;
  blocked-ok)
    _need_jq
    s="" reason=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --session) s="${2:-}"; shift; [ $# -gt 0 ] && shift ;;
        *) reason="$reason $1"; shift ;;
      esac
    done
    reason="$(printf '%s' "$reason" | sed 's/^ *//; s/ *$//')"
    if [ -z "$reason" ]; then
      echo "workaround-exhaustion blocked-ok: a reason is required — the specific route or permission you lack." >&2; exit 2
    fi
    _cli_init "$s"
    reason="$(_scrub "$reason")"
    mkdir -p "$run" 2>/dev/null || { echo "workaround-exhaustion: cannot create $run" >&2; exit 2; }
    jq -cn --arg ts "$(_now)" --arg r "$reason" '{schema_version:1, ts:$ts, blocked_ok:$r, actor:"agent"}' >> "$ledger" || exit 2
    _emit warn "cli" "workaround-blocked-ok"
    echo "logged blocked-ok for session $sid (a warn event was emitted — this is never silent)"
    ;;
  status|list)
    s=""
    while [ $# -gt 0 ]; do
      case "$1" in
        --session) s="${2:-}"; shift; [ $# -gt 0 ] && shift ;;
        *) shift ;;
      esac
    done
    _cli_init "$s"
    if [ "$sub" = "status" ]; then
      _need_jq
      _status_text
    elif [ -f "$ledger" ]; then
      cat "$ledger"
    else
      echo "(no ledger at $ledger)"
    fi
    ;;
  *)
    echo "usage: workaround-exhaustion.sh ask|stop | tried [--session S] --channel C [--tried yes|no] --result R --bypass-test B | blocked-ok [--session S] <reason> | status [--session S] | list [--session S]" >&2
    exit 2
    ;;
esac
