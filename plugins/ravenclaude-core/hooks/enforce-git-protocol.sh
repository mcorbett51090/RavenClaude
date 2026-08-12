#!/usr/bin/env bash
# enforce-git-protocol.sh
# PreToolUse hook for Bash. A DEFAULT-WARN, in-loop nudge toward this repo's own
# git conventions. It is advisory guidance, NOT a safety control — the safety
# floor is owned elsewhere (see "SCOPE / WHAT THIS DOES NOT DO" below).
#
# Exactly THREE checks, anchored to the MUTATING git subcommand token so a
# read-only git call (log / status / diff / show / fetch) never fires:
#
#   1. commit-message shape — on a `git commit` carrying an INLINE message (-m /
#      --message), WARN when the subject is not Conventional-Commits
#      `type(scope): subject` (types: feat|fix|chore|docs|refactor|test|build|ci|
#      perf|style|revert). Default warn; blocks (exit 2) ONLY when the knob is
#      `block`. A commit with no inline message (editor, or -F <file>) is not
#      inspected — there is no subject to see.
#   2. branch-name — on a NEW-BRANCH creation (checkout -b <name> / switch -c
#      <name> / plain `branch <name>`), WARN when <name> does not match the repo's
#      prefix convention `^(feat|fix|chore|docs|refactor|agent)/` (rules/git-workflow.md).
#      Default warn; blocks ONLY when the knob is `block`.
#   3. push-to-a-protected-branch — a direct, non-force push whose refspec targets
#      main / master is ADVISORY ONLY: it emits a nudge and NEVER blocks at any
#      knob value. This repo's own `main` ruleset is bypass_mode:always by design.
#
# KNOB — `git_protocol: off | warn | block` in
#   <project>/.ravenclaude/comfort-posture.yaml (read with the same minimal-scalar
#   sed idiom worktree-guard.sh uses for its `worktree_guard:` knob — no PyYAML).
#   Default `warn` WHEN THE POSTURE FILE IS PRESENT. If the posture file is ABSENT
#   the hook NO-OPS (this is opt-in, like every other comfort-posture-gated hook —
#   the reverse of a naive "default-fire everywhere" reading).
#
# FAIL-OPEN / NO-OP BY CONTRACT — any error, missing git, missing python3, an
#   unreadable or absent comfort-posture.yaml, or an unparseable command → exit 0
#   (allow). A default-warn advisory that cannot read its input must never block.
#
# SCOPE / WHAT THIS DOES NOT DO (deliberate, to avoid collision + double-firing):
#   * It does NOT touch force operations, branch force-delete, recursive-remove, or
#     hard reset — those are the destructive guard's job. A push carrying the force
#     flag (or a `+`-prefixed refspec) is force-EXCLUDED here so this hook can never
#     collide with that guard. Those verbs are referenced only as NOUNS above.
#   * It never blocks a push to main/master.
#   * No commit-body / length / trailer / casing pedantry; no secret scanning.
#
# PORTABILITY — must run on stock macOS bash 3.2.57. No `declare -A`, no `mapfile`,
#   no `${x^^}`, no `shopt -s globstar`, no GNU `timeout`, no `grep -P`, no `sed -i`.
#   See the four macOS-door milestones in the plugin CLAUDE.md.

set -uo pipefail   # NOT -e: a guard must not die mid-check (worktree-guard idiom).

# --- fail-safe event emitter (sourced; missing helper degrades to a no-op) -----
_emit_event_helper="$(dirname "$0")/_emit-event.sh"
if [ -f "$_emit_event_helper" ]; then
  # shellcheck source=/dev/null
  . "$_emit_event_helper" 2>/dev/null || true
fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

# --- read the command from the stdin JSON payload (jq preferred, python3 else) -
# `payload` is kept in scope so _emit-event.sh's _ee_resolve_session can read
# .session_id off it (native Claude Code carries the id only on the payload).
cmd=""
payload=""
if [ ! -t 0 ]; then
  payload="$(cat 2>/dev/null || true)"
  if [ -n "$payload" ]; then
    if command -v jq >/dev/null 2>&1; then
      cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty' 2>/dev/null || true)"
    elif command -v python3 >/dev/null 2>&1; then
      cmd="$(printf '%s' "$payload" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("tool_input",{}).get("command","") or "")
except Exception: pass' 2>/dev/null || true)"
    fi
  fi
fi
[ -z "$cmd" ] && exit 0

# --- cheap pre-filter: bail unless this even looks like a git mutating call -----
# Performance only — the python3 classifier below is authoritative about the
# subcommand position. A read-only git call (log/status/diff/show/fetch) carries
# none of these subcommand words and bails here at the cost of two greps.
printf '%s' "$cmd" | grep -Eq '(^|[^[:alnum:]_./-])git([^[:alnum:]_-]|$)' || exit 0
printf '%s' "$cmd" | grep -Eq 'commit|checkout|switch|branch|push' || exit 0

# --- knob: absent posture => no-op (opt-in); default warn; `off` => no-op -------
posture="${CLAUDE_PROJECT_DIR:-.}/.ravenclaude/comfort-posture.yaml"
[ -f "$posture" ] || exit 0
mode="$(sed -n 's/^[[:space:]]*git_protocol:[[:space:]]*\([A-Za-z]\{1,\}\).*/\1/p' "$posture" 2>/dev/null | head -1)"
[ -z "$mode" ] && mode="warn"
case "$mode" in off|warn|block) ;; *) mode="warn" ;; esac
[ "$mode" = "off" ] && exit 0

# --- the classifier needs python3 for shell-aware tokenization; absent => no-op -
command -v python3 >/dev/null 2>&1 || exit 0

# Classify the command. Output (on stdout) is at most one line:
#   <kind>\t<value>       kind in: commit-message | branch-name | push-to-main
# Empty output => nothing to flag. The command travels via the __GP_CMD env var,
# never interpolated into the program text. Loaded into a variable via a here-doc
# fed to `read` (a SIMPLE command) so macOS bash 3.2 does not mis-parse a here-doc
# nested inside $(); then run with `python3 -c` (no temp file).
IFS= read -r -d '' __GP_PY <<'PY' || :
import os, re, shlex, sys

cmd = os.environ.get("__GP_CMD", "")

# Conventional-Commits subject: type, optional (scope), optional ! , ": ", body.
CC_RE = re.compile(
    r"^(?:feat|fix|chore|docs|refactor|test|build|ci|perf|style|revert)"
    r"(?:\([^)]+\))?!?:\s.+"
)
# This repo's branch-prefix convention (rules/git-workflow.md).
BR_RE = re.compile(r"^(?:feat|fix|chore|docs|refactor|agent)/")

# git global options that consume a FOLLOWING value token when not =-attached.
_VALUE_GLOBALS = {"-C", "-c", "--git-dir", "--work-tree", "--namespace",
                  "--exec-path", "--config-env", "--super-prefix"}
_SEPARATORS = {";", "&&", "||", "|", "&"}


def git_invocations(tokens):
    """Yield (subcommand, args) for each `git <sub> ...` in the token stream."""
    n = len(tokens)
    i = 0
    while i < n:
        base = tokens[i].rsplit("/", 1)[-1]
        if base == "git":
            j = i + 1
            while j < n:
                g = tokens[j]
                if g == "--":
                    j += 1
                    break
                if g.startswith("-"):
                    if g in _VALUE_GLOBALS and "=" not in g:
                        j += 2
                    else:
                        j += 1
                    continue
                break
            if j < n:
                sub = tokens[j]
                args = []
                k = j + 1
                while k < n and tokens[k] not in _SEPARATORS:
                    args.append(tokens[k])
                    k += 1
                yield sub, args
                i = k
                continue
        i += 1


def commit_subject(args):
    i = 0
    while i < len(args):
        a = args[i]
        if a == "-m" or a == "--message":
            return args[i + 1] if i + 1 < len(args) else None
        if a.startswith("--message="):
            return a[len("--message="):]
        if a.startswith("-m") and len(a) > 2 and not a.startswith("--"):
            return a[2:]                      # glued short form, e.g. -msubject
        if re.match(r"^-[A-Za-z]*m$", a) and not a.startswith("--"):
            return args[i + 1] if i + 1 < len(args) else None   # bundle, e.g. -am
        i += 1
    return None


def new_branch_name(sub, args):
    positional = [a for a in args if not a.startswith("-")]
    flags = [a for a in args if a.startswith("-")]

    def has(*names):
        return any(f in names for f in flags)

    if sub == "checkout":
        for idx, a in enumerate(args):
            if a in ("-b", "-B") and idx + 1 < len(args):
                return args[idx + 1]
        return None
    if sub == "switch":
        for idx, a in enumerate(args):
            if a in ("-c", "-C", "--create", "--force-create") and idx + 1 < len(args):
                return args[idx + 1]
        return None
    if sub == "branch":
        # Only a PLAIN creation (`git branch <name>`). Anything that lists, deletes,
        # renames, copies, or edits is not a new-branch creation -> not our concern
        # (delete in particular is force-EXCLUDED — the destructive guard owns it).
        if has("-d", "-D", "--delete", "-m", "-M", "--move", "-c", "-C", "--copy",
               "-l", "--list", "-a", "--all", "-r", "--remotes",
               "--edit-description", "--show-current",
               "-u", "--set-upstream-to", "--unset-upstream"):
            return None
        return positional[0] if positional else None
    return None


def push_target(args):
    # force-EXCLUDE: this hook never touches force operations; leave them to the
    # destructive guard so the two can never collide or double-fire.
    for a in args:
        if a in ("--force", "--force-with-lease") or a.startswith("--force-with-lease="):
            return None
        if a.startswith("-") and not a.startswith("--") and "f" in a[1:]:
            return None                       # short-flag bundle carrying the force flag
    positional = [a for a in args if not a.startswith("-")]
    for a in positional:
        if a.startswith("+"):
            return None                       # +refspec force form — destructive guard's
        for side in [a] + a.split(":"):
            if side in ("main", "master"):
                return side
    return None


findings = []
try:
    tokens = shlex.split(cmd, comments=False, posix=True)
except ValueError:
    tokens = None

if tokens:
    for sub, args in git_invocations(tokens):
        if sub == "commit":
            subj = commit_subject(args)
            if subj is not None:
                first = subj.split("\n", 1)[0].strip()
                if first and not CC_RE.match(first):
                    findings.append(("commit-message", first))
        elif sub in ("checkout", "switch", "branch"):
            name = new_branch_name(sub, args)
            if name is not None and not BR_RE.match(name):
                findings.append(("branch-name", name))
        elif sub == "push":
            tgt = push_target(args)
            if tgt is not None:
                findings.append(("push-to-main", tgt))

# Priority so a blockable finding wins over the advisory one on a chained command:
# commit-message > branch-name > push-to-main.
_PRIO = {"commit-message": 0, "branch-name": 1, "push-to-main": 2}
if findings:
    findings.sort(key=lambda f: _PRIO[f[0]])
    kind, val = findings[0]
    sys.stdout.write(kind + "\t" + val.replace("\t", " ").replace("\n", " "))
PY

verdict="$(__GP_CMD="$cmd" python3 -c "$__GP_PY" 2>/dev/null || true)"
[ -z "$verdict" ] && exit 0

kind="$(printf '%s' "$verdict" | cut -f1)"
val="$(printf '%s' "$verdict" | cut -f2-)"

reason=""
nudge=""
remediation=""
blockable=0
case "$kind" in
  commit-message)
    reason="commit-message-not-conventional"
    nudge="[enforce-git-protocol] commit subject is not Conventional Commits ('type(scope): subject'): \"$val\""
    remediation="[enforce-git-protocol] Try e.g. 'fix(scope): <subject>' — types: feat|fix|chore|docs|refactor|test|build|ci|perf|style|revert (see rules/git-workflow.md)."
    blockable=1
    ;;
  branch-name)
    reason="branch-name-off-convention"
    nudge="[enforce-git-protocol] new branch '$val' does not match the repo's prefix convention (feat|fix|chore|docs|refactor|agent)/…"
    remediation="[enforce-git-protocol] Rename to e.g. 'feat/$val' (see rules/git-workflow.md)."
    blockable=1
    ;;
  push-to-main)
    reason="push-to-protected-branch"
    nudge="[enforce-git-protocol] advisory: this pushes directly to '$val'. Prefer a feature branch + PR. (advisory only — never blocked)"
    remediation=""
    blockable=0
    ;;
  *)
    exit 0
    ;;
esac

# block mode + a blockable finding => deny (exit 2). Everything else is a
# non-blocking stderr nudge (exit 0): warn mode, and push-to-main at ANY mode.
if [ "$blockable" = "1" ] && [ "$mode" = "block" ]; then
  _emit_hook_event "enforce-git-protocol.sh" "deny" "Bash" "$cmd" "$reason" 2
  {
    printf '%s\n' "$nudge"
    [ -n "$remediation" ] && printf '%s\n' "$remediation"
    printf '%s\n' "[enforce-git-protocol] To allow this style, set 'git_protocol: warn' (or 'off') in .ravenclaude/comfort-posture.yaml."
  } >&2
  exit 2   # 2 blocks the tool call; 1 would NOT (non-blocking error)
fi

_emit_hook_event "enforce-git-protocol.sh" "warn" "Bash" "$cmd" "$reason" 0
{
  printf '%s\n' "$nudge"
  [ -n "$remediation" ] && printf '%s\n' "$remediation"
} >&2
exit 0
