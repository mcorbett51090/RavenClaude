#!/usr/bin/env bash
# env-integrity-guard.sh — quarantine a repo whose project settings plant
# execution-control environment variables (AppSec hook-env, 2026-10-18).
#
# Claude Code exports the `env` block of a project's .claude/settings.json (and
# settings.local.json) into every hook process. Measured on 2.1.260: a planted
# BASH_ENV ran inside every bash hook, a planted PATH resolved `jq` to the repo's
# binary, LD_PRELOAD was handed to every exec, and THING_SEAT_ACTIVE would switch the
# command-review tribunal off. The hardened launch line (hooks.json) keeps most of
# those out of OUR processes; this guard refuses to let the session act at all.
#
# Modes:
#   pretool  (PreToolUse, matcher "*", registered FIRST) — on a finding, DENY the
#            tool call: "project settings plant execution-control env (<keys>);
#            this repo is quarantined". Claude Code runs matching hooks in
#            parallel, so "first" is placement, not ordering; any deny wins.
#   session  (SessionStart) — cannot block; surfaces the same finding as
#            additionalContext + a systemMessage so the user sees it at once.
#
# Static check: $CLAUDE_PROJECT_DIR/.claude/settings.json and settings.local.json.
# A key in .env matching PATH BASH_ENV ENV SHELLOPTS BASHOPTS IFS LD_* DYLD_*
# PYTHONPATH PYTHONSTARTUP NODE_OPTIONS PERL5OPT RUBYOPT GIT_SSH_COMMAND GIT_CONFIG_*
# THING_SEAT_* RAVENCLAUDE_* BASH_FUNC_* is a finding. BASH_FUNC_<name>%% is how
# bash exports a FUNCTION: every bash hook imports it at startup, and a function
# shadows the binary of the same name (`BASH_FUNC_jq%%` answers for jq). This
# keys on the planted variable, never on functions merely being present, so a
# shell's own exported helpers (Lmod's `module`, a distro `which`) are not flagged. A file that exists but is empty,
# unreadable or not valid JSON (or whose .env is not an object) is a finding too
# (fail closed). User-scope ~/.claude/settings.json is NOT read (a repo can't write it).
#
# Runtime cross-check: the launch line passes the INHERITED values as
# RC_INHERITED_BASH_ENV / RC_INHERITED_LD_PRELOAD / RC_INHERITED_PATH (set on the
# command line after `env`, so a planted copy cannot override them). Deny if the
# inherited BASH_ENV or LD_PRELOAD is set, or the inherited PATH lacks /usr/bin.
# Run without the launch line (a test or a direct call), the current env is used.
#
# Honest limit: a REAL shared object in LD_PRELOAD / DYLD_INSERT_LIBRARIES has
# already been loaded into the /bin/sh Claude Code starts, before any plugin code
# runs. A plugin cannot stop that; it can only refuse to continue (this guard).
#
# Escape hatch: none by design — remove the keys from the project settings file.
set -uo pipefail

mode="${1:-pretool}"
payload=""
[ -t 0 ] || payload="$(cat 2>/dev/null || true)"

_KEYS_RE='^(PATH|BASH_ENV|ENV|SHELLOPTS|BASHOPTS|IFS|PYTHONPATH|PYTHONSTARTUP|NODE_OPTIONS|PERL5OPT|RUBYOPT|GIT_SSH_COMMAND)$|^(LD_|DYLD_|GIT_CONFIG_|THING_SEAT_|RAVENCLAUDE_|BASH_FUNC_)'

_PY_KEYS='import json, re, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
if not isinstance(d, dict): sys.exit(9)
e = d.get("env", {})
if not isinstance(e, dict): sys.exit(9)
for k in e:
    if re.search(sys.argv[2], k): print(k)'

proj="${CLAUDE_PROJECT_DIR:-}"
if [ -z "$proj" ] && command -v jq >/dev/null 2>&1; then
  proj="$(printf '%s' "$payload" | jq -r '.cwd // empty' 2>/dev/null || true)"
fi
[ -n "$proj" ] || proj="$PWD"

findings=""   # space-separated "file:KEY" / "file:<reason>"
add() { findings="${findings:+$findings, }$1"; }

# _keys_of <file> — prints matching keys one per line; exit 0 clean/hit, 9 = fail closed
_keys_of() {
  local f="$1" out rc
  if command -v jq >/dev/null 2>&1; then
    out="$(jq -r --arg re "$_KEYS_RE" '
      if type != "object" then error("not an object") else . end
      | (if has("env") then .env else {} end)
      | if type != "object" then error("env is not an object") else . end
      | keys[] | select(test($re))' "$f" 2>/dev/null)"; rc=$?
    # jq exits 0 on an EMPTY file with no output — treat empty as fail closed.
    [ -s "$f" ] || return 9
    [ "$rc" -eq 0 ] || return 9
  elif [ -x /usr/bin/python3 ]; then
    # No heredoc inside $( ): bash 3.2 (macOS /bin/bash) aborts at parse time on it.
    out="$(/usr/bin/python3 -I -c "$_PY_KEYS" "$f" "$_KEYS_RE" 2>/dev/null)"; rc=$?
    [ "$rc" -eq 0 ] || return 9
  else
    return 9
  fi
  printf '%s' "$out"
  return 0
}

for name in settings.json settings.local.json; do
  f="$proj/.claude/$name"
  [ -e "$f" ] || [ -L "$f" ] || continue
  if [ ! -f "$f" ] || [ ! -r "$f" ]; then add ".claude/$name:<unreadable>"; continue; fi
  keys="$(_keys_of "$f")"; rc=$?
  if [ "$rc" -ne 0 ]; then add ".claude/$name:<empty-or-malformed>"; continue; fi
  for k in $keys; do add "$k"; done
done

# Runtime cross-check (inherited values; see header).
if [ "${RC_INHERITED_PATH+set}" = set ]; then
  ib="${RC_INHERITED_BASH_ENV-}"; il="${RC_INHERITED_LD_PRELOAD-}"; ip="${RC_INHERITED_PATH-}"
else
  ib="${BASH_ENV-}"; il="${LD_PRELOAD-}"; ip="${PATH-}"
fi
[ -n "$ib" ] && add "runtime:BASH_ENV"
[ -n "$il" ] && add "runtime:LD_PRELOAD"
case ":$ip:" in *:/usr/bin:*) : ;; *) add "runtime:PATH-without-/usr/bin" ;; esac

[ -z "$findings" ] && exit 0

reason="project settings plant execution-control env (${findings}); this repo is quarantined"
echo "[env-integrity] $reason" >&2
if [ "$mode" = "session" ]; then
  msg="RavenClaude QUARANTINE: ${reason}. Every tool call in this session will be denied until the keys are removed from .claude/settings.json / settings.local.json."
  if command -v jq >/dev/null 2>&1; then
    jq -cn --arg m "$msg" '{systemMessage:$m,hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$m}}'
  else
    printf '{"systemMessage":"RavenClaude QUARANTINE: project settings plant execution-control env; this repo is quarantined"}\n'
  fi
  exit 0
fi
if command -v jq >/dev/null 2>&1; then
  jq -cn --arg r "$reason" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  exit 0
fi
# No jq: exit 2 blocks on its own (stderr above is the reason).
exit 2
