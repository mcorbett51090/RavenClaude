#!/usr/bin/env bash
# runaway-brake.sh — PreToolUse deterministic runaway / rabbit-hole brake.
#
# Replaces the native Claude Code `auto`-mode 3-consecutive / 20-total block
# brake, which is Anthropic-API/Claude-only and therefore UNAVAILABLE under
# GitHub Copilot CLI (Claude + ChatGPT + Grok routing). This is the portable,
# model-agnostic equivalent: it counts tool calls per session and trips when the
# agent THRASHES (too many byte-identical calls in a row — the "looping on a
# fabricated error" rabbit-hole signal) or blows a generous total-call ceiling.
#
# No-ops (allow, exit 0) unless .ravenclaude/comfort-posture.yaml exists, so a
# non-adopter pays nothing (one stat). Opt out entirely with `runaway: off`.
# Tune with:
#   runaway:
#     max_consecutive: 8     # identical calls in a row before tripping
#     max_total: 1200         # total tool calls this session before tripping
#
# Deterministic: no model in the loop. Ports to Copilot via the bash-pretool
# adapter (a Claude exit-2 block -> a Copilot deny). State is a per-session
# counter file under .ravenclaude/runs/thing/runaway/ (the same per-session
# pattern the tribunal's fatigue counter uses); a new session_id starts fresh.

set -uo pipefail

command -v jq >/dev/null 2>&1 || exit 0
payload=""
[ ! -t 0 ] && payload="$(cat)"
[ -z "$payload" ] && exit 0

cwd="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null)"
[ -z "$cwd" ] && cwd="$PWD"
posture="${cwd}/.ravenclaude/comfort-posture.yaml"
[ -f "$posture" ] || exit 0   # not opted in -> zero cost

# Explicit opt-out.
grep -Eq '^[[:space:]]*runaway:[[:space:]]*off[[:space:]]*$' "$posture" 2>/dev/null && exit 0

max_consec="$(sed -n 's/^[[:space:]]*max_consecutive:[[:space:]]*\([0-9]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
max_total="$(sed -n 's/^[[:space:]]*max_total:[[:space:]]*\([0-9]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
[ -z "$max_consec" ] && max_consec=8
[ -z "$max_total" ] && max_total=1200

sid="$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null)"
[ -z "$sid" ] && exit 0
safe_sid="$(printf '%s' "$sid" | tr -dc 'A-Za-z0-9._-' | cut -c1-128)"
[ -z "$safe_sid" ] && exit 0

dir="${cwd}/.ravenclaude/runs/thing/runaway"
mkdir -p "$dir" 2>/dev/null || exit 0
f="${dir}/${safe_sid}"

# Stable hash of this tool call (name + sorted input).
h="$(printf '%s' "$payload" | jq -cS '{t:(.tool_name//""),i:(.tool_input//{})}' 2>/dev/null | cksum | cut -d' ' -f1)"
[ -z "$h" ] && h="0"

# ── READ-ONLY CARVE-OUT ───────────────────────────────────────────────────────
# A call with NO blast radius shouldn't count toward the consecutive-LOOP counter
# (a legitimate read-only startup burst — repeated `git log`, `ls`, `cat` — is not
# a runaway). Such a call is TRANSPARENT to the loop detector: it neither
# increments nor resets `consec`. It STILL increments `total` (the session ceiling
# stays intact for every call regardless of type). Fail-closed: any doubt, or any
# classification error, treats the call as NOT read-only (it counts).
#
# A call is read-only iff:
#   tool_name ∈ {Read, Grep, Glob, NotebookRead}
#   OR (tool_name == "Bash" AND the command matches a STRICT, ANCHORED allowlist).
# The Bash allowlist is conservative — only obviously-non-mutating commands,
# anchored at the start of the (single) command. ANY shell metacharacter that
# could chain to a mutating command (`&&`, `;`, `|`, backtick, `$(`, `>`, `<`),
# or any mutating token anywhere in the string (rm/mv/cp/sed -i/tee/install/
# deploy/git push|commit|checkout|...), forces NOT read-only.
is_read_only() {
  ro_tn="$1"; ro_cmd="$2"
  case "$ro_tn" in
    Read|Grep|Glob|NotebookRead) return 0 ;;
    Bash) : ;;          # fall through to the command allowlist
    *) return 1 ;;
  esac
  # Empty / unreadable command → not read-only (fail closed).
  [ -z "$ro_cmd" ] && return 1

  # Reject any shell-control / redirection / substitution metacharacter outright.
  # These are the vectors by which a "read-only-looking" prefix chains to a
  # mutating command (`git log && rm x`, `cat f > g`, `echo $(rm x)`, `a | tee b`).
  case "$ro_cmd" in
    *'&'*|*';'*|*'|'*|*'>'*|*'<'*|*'`'*|*'$('*|*'${'*|*$'\n'*) return 1 ;;
  esac

  # Reject any explicitly-mutating token ANYWHERE in the command (defence in depth;
  # the metachar reject above already blocks most chaining, this catches the rest
  # e.g. a flag value or an unusual-but-mutating single command).
  case " $ro_cmd " in
    *' rm '*|*' rmdir '*|*' mv '*|*' cp '*|*' tee '*|*' dd '*|*' truncate '*|\
    *' install '*|*' deploy '*|*' chmod '*|*' chown '*|*' ln '*|*' mkdir '*|\
    *' touch '*|*' kill '*|*' pkill '*|*' npm '*|*' npx '*|*' pip '*|*' pip3 '*|\
    *' apt '*|*' apt-get '*|*' yum '*|*' brew '*|*' curl '*|*' wget '*|\
    *'sed -i'*|*'git push'*|*'git commit'*|*'git checkout'*|*'git reset'*|\
    *'git merge'*|*'git rebase'*|*'git tag'*|*'git branch -'*|*'git add'*|\
    *'git rm'*|*'git mv'*|*'git stash'*|*'git clean'*|*'git apply'*|\
    *'git restore'*|*'git switch'*|*'git cherry-pick'*|*'git revert'*|\
    *'git update-ref'*|*'git gc'*|*'git fetch'*|*'git pull'*) return 1 ;;
  esac

  # Match the FIRST token (the program) against the strict anchored allowlist.
  ro_first="${ro_cmd%%[[:space:]]*}"
  ro_rest="${ro_cmd#"$ro_first"}"
  ro_rest="${ro_rest#"${ro_rest%%[![:space:]]*}"}"   # left-trim remaining args

  case "$ro_first" in
    ls|pwd|echo|cat|head|tail|wc|stat|file|which|find|grep|jq) return 0 ;;
    command)
      # only `command -v ...` (a lookup) is read-only
      case "$ro_rest" in -v\ *|-v) return 0 ;; *) return 1 ;; esac ;;
    bash)
      # only `bash -n ...` (syntax check, no execution) is read-only
      case "$ro_rest" in -n\ *) return 0 ;; *) return 1 ;; esac ;;
    node)
      # only `node --check ...` (syntax check, no execution) is read-only
      case "$ro_rest" in --check\ *) return 0 ;; *) return 1 ;; esac ;;
    python3|python)
      # only `python3 -m json.tool ...` (a read/validate) is read-only
      case "$ro_rest" in -m\ json.tool*) return 0 ;; *) return 1 ;; esac ;;
    git)
      # strict anchored read-only git subcommands only
      case "$ro_rest" in
        log|log\ *|status|status\ *|diff|diff\ *|show|show\ *|\
        branch|branch\ *|remote|remote\ *|rev-parse|rev-parse\ *|\
        ls-files|ls-files\ *|describe|describe\ *|\
        config\ --get|config\ --get\ *|config\ --list|config\ --list\ *) return 0 ;;
        *) return 1 ;;
      esac ;;
    *) return 1 ;;
  esac
}

tn="$(printf '%s' "$payload" | jq -r '.tool_name // ""' 2>/dev/null)"
cmd=""
if [ "$tn" = "Bash" ]; then
  cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // ""' 2>/dev/null)"
fi
read_only=0
if is_read_only "$tn" "$cmd"; then read_only=1; fi

total=0; last="-"; consec=0
if [ -r "$f" ]; then
  read -r total last consec < "$f" 2>/dev/null || { total=0; last="-"; consec=0; }
fi
case "$total" in (*[!0-9]*|"") total=0;; esac
case "$consec" in (*[!0-9]*|"") consec=0;; esac

# `total` ALWAYS increments (the ceiling bounds every session regardless of type).
total=$((total + 1))

if [ "$read_only" = "1" ]; then
  # Transparent to the loop detector: do NOT touch `consec`, and preserve `last`
  # so a mutating command repeated either side of a read-only burst still chains.
  printf '%s %s %s\n' "$total" "$last" "$consec" > "$f" 2>/dev/null || true
else
  if [ "$h" = "$last" ]; then consec=$((consec + 1)); else consec=1; fi
  printf '%s %s %s\n' "$total" "$h" "$consec" > "$f" 2>/dev/null || true
fi

trip=""
if [ "$consec" -ge "$max_consec" ]; then
  trip="repeated the same tool call ${consec} times in a row (limit ${max_consec})"
elif [ "$total" -ge "$max_total" ]; then
  trip="made ${total} tool calls this session (limit ${max_total})"
fi

if [ -n "$trip" ]; then
  printf '%s\n' "Runaway brake: the agent ${trip}. Paused to prevent a rabbit hole / runaway. Intervene, or raise the limit under \`runaway:\` in .ravenclaude/comfort-posture.yaml (or set \`runaway: off\`)." >&2
  exit 2
fi
exit 0
