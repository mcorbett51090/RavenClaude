#!/usr/bin/env bash
# guard-destructive.sh
# PreToolUse hook for Bash. Catches obviously destructive commands that
# slipped past the deny-list (e.g. inside subshells, pipes, here-docs).
#
# Input:  the tool call as JSON on stdin — {"tool_input": {"command": "..."}}
#         (the canonical Claude Code hook contract). Falls back to $1 for any
#         legacy registration that still passes the command as a positional arg.
# Output: exit 2 to BLOCK the command (stderr is fed back to the model).
#         NOTE: exit 2 is the ONLY blocking code — Claude Code treats exit 1
#         (and every other non-zero) as a NON-blocking error and runs the
#         command anyway. See code.claude.com/docs/en/hooks ("Exit 2 ... blocks
#         the tool call"). This hook previously exited 1 and read $1, neither of
#         which actually blocked; migrated to stdin-JSON + exit-2 (tribunal T0).
#
# Matching is done against a NORMALIZED form of the command (quotes stripped,
# ${HOME} folded to $HOME, whitespace collapsed) so that trivial variants can't
# dodge a literal pattern. Two-panel audit (2026-05-31) found the prior literal
# patterns were bypassed by idiomatic forms — `rm -fr` (flag order), `rm -rf
# ${HOME}` (brace expansion), `git push origin +HEAD:main` (refspec force-push),
# `curl … | sudo bash` / `bash <(curl …)` (pipe-to-shell variants), `git branch
# -D`, and whole-disk ops (`mkfs`/`shred`/`dd of=/dev/disk0`). This hook is the
# consumer's PRIMARY deterministic guard on the `/plugin install` path (the
# settings.json deny-list is marketplace-dev-only), so the variants matter.
#
# SCOPE (2026-07-08 review): this is a command-STRING scanner. It catches destructive
# content within a SINGLE command — including a heredoc that writes a file and then
# executes it in the SAME command (`cat <<'EOF' > f; rm -rf /; EOF; bash f`, closed by
# the write-then-execute branch in the normalizer). It CANNOT see write-then-execute
# spread ACROSS separate tool calls (Write a script in one call, `bash` it in another) —
# a string scanner has no visibility into the other call, and the target is reachable via
# Write/printf/tee/base64 regardless. That boundary is the OS container/worktree, NOT this
# hook — see the plugin CLAUDE.md "Containment posture — the boundary the tribunal
# structurally can't provide" section. Do not attempt to close it here.

set -euo pipefail

# Structured hook-event substrate (P0.2). Sourced fail-safe — a missing helper
# becomes a no-op so the emit call below can never throw or block the verdict.
_emit_event_helper="$(dirname "$0")/_emit-event.sh"
if [ -f "$_emit_event_helper" ]; then
  # shellcheck source=/dev/null
  . "$_emit_event_helper" 2>/dev/null || true
fi
command -v _emit_hook_event >/dev/null 2>&1 || _emit_hook_event() { :; }

# Prefer stdin JSON (canonical); fall back to the positional arg (legacy).
cmd=""
payload=""
if [ ! -t 0 ]; then
  payload="$(cat)"
  if [ -n "$payload" ]; then
    if command -v jq >/dev/null 2>&1; then
      cmd="$(printf '%s' "$payload" | jq -r '.tool_input.command // empty' 2>/dev/null || true)"
    elif command -v python3 >/dev/null 2>&1; then
      # jq-free fallback: this is the consumer's PRIMARY destructive guard, so it
      # must NOT silently no-op when jq is absent (it previously read cmd="" and
      # exited 0 = allow-all, with no warning — 2026-07 review).
      cmd="$(printf '%s' "$payload" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("tool_input",{}).get("command","") or "")
except Exception: pass' 2>/dev/null || true)"
    fi
  fi
fi
[ -z "$cmd" ] && cmd="${1:-}"
# If a non-empty payload arrived but we could not extract a command (neither jq
# nor python3 available), warn LOUDLY rather than fail open silently. We cannot
# fail-closed-deny here (that would block every Bash call on a host missing both
# parsers, breaking the session) — but a visible warning means the guard is never
# silently inert, matching the fail-safe posture of the sibling guards.
if [ -z "$cmd" ] && [ -n "$payload" ]; then
  printf '%s\n' "[guard-destructive] WARNING: could not parse the command (jq and python3 both unavailable); the destructive-command guard is DEGRADED for this call." >&2
fi
[ -z "$cmd" ] && exit 0

# --- Normalization ---------------------------------------------------------
# Canonicalize so flag-order / quoting / brace-expansion variants converge on
# one form before matching. We match against the NORMALIZED string.
#
# Step 0 (added 2026-06-03): strip TEXT-CONTENT regions that don't represent
# command intent. Two classes:
#   (a) `-m "..."` / `-m '...'` message bodies (the `git commit -m` case
#       and any other tool that takes a `-m` message arg) — these are
#       documentation text the user writes; if they describe a destructive
#       command (e.g. quoting `git branch -D` in the changelog), the LITERAL
#       command is not being executed and must not trigger the guard.
#   (b) Heredoc bodies — `<<TAG ... TAG` blocks delivered as multi-line text
#       (e.g. `cat <<EOF > file ... EOF`). The body is data written to a file,
#       not commands executed. Same false-positive surface as (a).
# Both regressions were observed 2026-06-03: a `git commit -m` and a heredoc
# body each contained the literal string `git branch -D` describing the
# escape-hatch script, and the guard incorrectly fired.
#
# Known unresolved limitation: a bare `echo "..."` or other quoted-string
# argument that contains a destructive pattern STILL triggers the guard,
# because the wholesale quote-stripping below (anti-obfuscation) is intentional
# — `rm -rf "/"` must continue to match `rm -rf /`. Extending the exemption
# from `-m` to `echo`/`printf` would open a new bypass surface (the very
# mechanism that makes those safe — quoted text output — is the same one that
# attackers use to smuggle destructive payloads through `echo "rm -rf /" |
# bash`). Workaround: write the documentation via the Write tool or via
# `git commit -F file`, not via a quoted shell argument.
#
# This step happens BEFORE the existing wholesale quote-stripping (which is
# doing real anti-obfuscation work — `rm -rf "/"` must still match `rm -rf /`).
norm="$cmd"
if command -v python3 >/dev/null 2>&1; then
  # Pass the raw command via env var to avoid the script's own heredoc EOF
  # marker interfering with heredocs INSIDE the command-under-inspection.
  #
  # The Python source is read into a variable via `read -d ''` and run with
  # `python3 -c` rather than piped through a `<<'PY'` heredoc INSIDE a $( ... )
  # command substitution. That older form is a bash parse hazard: the $()
  # scanner walks the heredoc body to find the matching `)`, and the Python
  # source's apostrophes / $'...' regex desync its paren counter, so it reads a
  # `)` inside the body as the close of the substitution and dies with a
  # "syntax error near unexpected token `)'" AT PARSE TIME — which aborts the
  # whole hook and blocks every Bash tool call (and can wedge session startup).
  # `read -d ''` is parse-safe (heredoc not nested in $()); `|| true` keeps its
  # EOF-return non-zero from tripping set -e.
  IFS= read -r -d '' __GUARD_PY <<'PY' || true
import re, sys, os
s = os.environ.get("__GUARD_RAW_CMD", "")
# A quoted body "executes" only if it carries command substitution — $(...) or a
# backtick. Parameter expansion (${VAR}) does not run a command in the common case,
# and the exotic bash-5.2 funsub ${ ...;} is out of scope for this defense-in-depth
# layer. Keeping the trigger to the two real command-execution vectors preserves the
# false-positive protection this stripping exists for: a -m / heredoc body that
# merely *documents* `git branch -D` / `rm -rf` must still be stripped, or this repo
# — whose commits and heredocs constantly quote destructive patterns — locks up.
_EXECUTES = re.compile(r"\$\(|`")
# (a) Strip -m "..." and -m '...' argument bodies so a commit message that documents
# a destructive pattern isn't itself flagged. A SINGLE-quoted body is inert (no shell
# expansion) and is always stripped. A DOUBLE-quoted body still expands $(...)/`...`
# at run time, so it is stripped ONLY when it carries no command substitution —
# otherwise `git commit -m "$(rm -rf ~)"` would be blanked to MSG before the scan
# below ever sees the live payload bash will execute (the hidden-substitution bypass).
def _strip_dq_m(m):
    return m.group(1) + "MSG" if not _EXECUTES.search(m.group(2)) else m.group(0)
s = re.sub(r'''(-m\s+)"([^"\n]*)"''', _strip_dq_m, s)
s = re.sub(r"""(-m\s+)'[^'\n]*'""", r"\1MSG", s)
# (b) Strip heredoc bodies (data written to a file, not executed) — but ONLY when the
# body is genuinely inert. A QUOTED delimiter (<<'TAG' / <<"TAG") suppresses all
# expansion, so its body is always stripped; a BARE <<TAG still expands $(...)/`...`
# at run time, so its body is stripped only when it carries no command substitution.
# Without this split, `cat <<EOF > f\n$(rm -rf ~)\nEOF` would be blanked before the
# scan, while bash still runs the substitution while building the heredoc.
# (b0) A heredoc feeding an INTERPRETER (`bash <<EOF … EOF`, `python3 <<'PY' … PY`,
# `sh <<X … X`) is NOT data-written-to-a-file — the body IS the script the shell
# executes, so blanking it would let `bash <<EOF\nrm -rf /\nEOF` slip past every
# deny pattern (the interpreter-heredoc fail-open closed by the 2026-07 review;
# the internal inconsistency that flagged it: `<(curl` / `$(curl` to a shell ARE
# caught, but the equivalent heredoc-to-shell was not). Detect it by the command
# word that opens the current simple command (after the nearest separator before
# `<<`), skipping leading VAR=val assignments, a leading `env`, and a leading `\`
# alias-suppressor; when it's an interpreter, do NOT strip — scan the body as code.
_INTERP_BASE = re.compile(
    r"^(?:sh|bash|dash|zsh|ksh|ash|csh|tcsh|mksh|busybox|python[0-9.]*|perl|ruby|node|php|tclsh|lua|Rscript)$"
)
def _heredoc_feeds_interpreter(prefix):
    seg = re.split(r"[\n;&|(]", prefix)[-1]
    toks = seg.split()
    i = 0
    while i < len(toks) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[i]):
        i += 1
    if i < len(toks) and toks[i].lstrip("\\").rsplit("/", 1)[-1] == "env":
        i += 1
        while i < len(toks) and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[i]):
            i += 1
    if i >= len(toks):
        return False
    base = toks[i].lstrip("\\").rsplit("/", 1)[-1]
    return bool(_INTERP_BASE.match(base))
# (b1) SAME-COMMAND write-then-execute (2026-07-08 review, finding 11). A heredoc that
# writes to a FILE with a non-interpreter command word (`cat <<'EOF' > /tmp/x.sh`) is
# inert data on its own — but if the SAME command string then executes that written file
# via an interpreter (`bash /tmp/x.sh`, `sh -x /tmp/x.sh`, `source /tmp/x.sh`, `. f`,
# `./x.sh`), the body IS run and blanking it would let `cat <<'EOF' > f; rm -rf /; EOF;
# bash f` slip every deny pattern. So when the redirect target is later executed in the
# same command, do NOT blank — leave the body for the structural/deny checks (mirrors the
# _heredoc_feeds_interpreter branch). SCOPE: this closes the SINGLE-command variant only.
# Write-then-execute ACROSS separate tool calls (Write a file in one call, `bash` it in
# another) is OUT OF SCOPE by design — a command-string scanner cannot see the other call,
# and the file is reachable via Write/printf/tee/base64 anyway; the OS container/worktree
# is that boundary (see the plugin CLAUDE.md "Containment posture" section).
_HEREDOC_REDIR_TARGET = re.compile(r">>?\s*(['\"]?)([^\s'\";|&<>()]+)\1")
_INTERP_EXEC_WORD = r"(?:sh|bash|dash|zsh|ksh|ash|busybox|source)"
def _cmd_executes_path(full, path):
    if not path:
        return False
    p = re.escape(path)
    base = re.escape(path.rsplit("/", 1)[-1])
    pat = re.compile(
        r"\b" + _INTERP_EXEC_WORD + r"\b[^\n;|&]*?" + p          # bash [flags] <path>
        + r"|(?<![\w/.])\.\s+[^\n;|&]*?" + p                      # . [flags] <path>
        + r"|(?:^|[\s;&|])\./" + base + r"(?![\w.])"              # ./<base>
    )
    return bool(pat.search(full))
def _strip_heredoc(m):
    quoted, body = m.group(1), m.group(3)
    prefix = m.string[: m.start()]
    if _heredoc_feeds_interpreter(prefix):
        return m.group(0)  # interpreter heredoc: body IS executed — scan it, don't blank
    # Look for the redirect target on this simple command (either before `<<`, in the
    # prefix's last segment, or after it, in the heredoc's opening line).
    seg = re.split(r"[\n;&|(]", prefix)[-1]
    opening = m.group(0).split("\n", 1)[0]
    tgt = _HEREDOC_REDIR_TARGET.search(seg + " " + opening)
    if tgt and _cmd_executes_path(m.string, tgt.group(2)):
        return m.group(0)  # written-then-executed in the same command — scan the body
    if quoted or not _EXECUTES.search(body):
        return "<<HEREDOC"
    return m.group(0)
s = re.sub(
    r"""<<-?\s*(['"]?)(\w+)\1[^\n]*\n([\s\S]*?)\n\s*\2\s*(?=\n|$)""",
    _strip_heredoc,
    s,
)
# (c) Decode bash ANSI-C $'...' quoting BEFORE the literal quote-stripping below.
# bash expands `$'\057'` -> `/`, `$'\053'` -> `+`, etc. at execution time, so a
# command can smuggle a destructive target/refspec past every whitespace- or
# literal-anchored pattern by writing it as octal/hex/unicode escapes
# (`rm -rf $'\057'`, `git push origin $'\053HEAD:main'`). Fold each $'...' token
# to the byte string bash would actually run so the matchers see the real command.
# Covers \nnn (octal), \xHH (hex), \u/\U (unicode) and the common letter escapes;
# an unknown escape degrades to the char after the backslash. This never raises
# (bad values are swallowed) — a decode failure leaves `norm` at the pre-decode
# form, i.e. no worse than before this block existed.
def _ansi_c_decode(m):
    body = m.group(1)
    simple = {"a": "\a", "b": "\b", "e": "\x1b", "E": "\x1b", "f": "\f",
              "n": "\n", "r": "\r", "t": "\t", "v": "\v", "\\": "\\",
              "'": "'", '"': '"', "?": "?"}
    out = []
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body):
            nxt = body[i + 1]
            if nxt in simple:
                out.append(simple[nxt]); i += 2; continue
            if nxt == "x":
                j, hexd = i + 2, ""
                while j < len(body) and len(hexd) < 2 and body[j] in "0123456789abcdefABCDEF":
                    hexd += body[j]; j += 1
                if hexd:
                    out.append(chr(int(hexd, 16))); i = j; continue
            if nxt in "uU":
                width = 4 if nxt == "u" else 8
                j, hexd = i + 2, ""
                while j < len(body) and len(hexd) < width and body[j] in "0123456789abcdefABCDEF":
                    hexd += body[j]; j += 1
                if hexd:
                    try:
                        out.append(chr(int(hexd, 16)))
                    except (ValueError, OverflowError):
                        pass
                    i = j; continue
            if nxt in "01234567":
                j, octd = i + 1, ""
                while j < len(body) and len(octd) < 3 and body[j] in "01234567":
                    octd += body[j]; j += 1
                try:
                    out.append(chr(int(octd, 8) & 0xFF))
                except ValueError:
                    pass
                i = j; continue
            out.append(nxt); i += 2; continue
        out.append(ch); i += 1
    return "".join(out)

s = re.sub(r"\$'((?:\\.|[^'\\])*)'", _ansi_c_decode, s)
sys.stdout.write(s)
PY
  __preproc="$(__GUARD_RAW_CMD="$norm" python3 -c "$__GUARD_PY" 2>/dev/null)" || __preproc=""
  # Only apply the preprocessed form if Python succeeded and produced output.
  # NB: the `|| __preproc=""` above is load-bearing — without it, a non-zero
  # exit from the python3 heredoc (e.g. an exotic UnicodeEncodeError) would trip
  # `set -e` and ABORT the whole guard before the deny checks run, and Claude
  # Code treats a non-2 hook exit as non-blocking → the destructive command
  # would run unchecked. Failing the substitution just falls back to `norm`.
  [ -n "$__preproc" ] && norm="$__preproc"
fi
norm="${norm//\"/}"                 # drop double quotes:  rm -rf "/"  -> rm -rf /
norm="${norm//\'/}"                 # drop single quotes
norm="${norm//\$\{HOME\}/\$HOME}"   # ${HOME} -> $HOME  (one form to match)
# Anti-obfuscation (added after the 2026-07 three-panel review): a command can
# smuggle a destructive payload past a whitespace-anchored pattern by writing the
# spaces as ${IFS}/$IFS (word-splitting still runs them as real separators) or by
# prefixing the command with a backslash (\rm still resolves to rm — the backslash
# only suppresses alias expansion). Fold both to their executed form BEFORE the
# whitespace collapse so the matchers see the same command the shell would run.
norm="${norm//\$\{IFS\}/ }"         # ${IFS} -> space
norm="${norm//\$IFS/ }"             # $IFS  -> space
norm="${norm//\\/}"                 # drop backslashes:  \rm -rf /  -> rm -rf /
norm="$(printf '%s' "$norm" | tr -s '[:space:]' ' ')"   # collapse whitespace runs

# Strip git GLOBAL options that sit between `git` and its subcommand (added after
# the 2026-07 review): `git -c foo=bar push --force`, `git --git-dir=.git push …`,
# `git -C path reset --hard` etc. would otherwise dodge every `git[[:space:]]+<sub>`
# anchor. Fold `git <globals…> <sub>` back to `git <sub>` so the subcommand
# patterns match. Fail-safe: any sed error leaves `norm` untouched.
#
# The strip is tolerant of ANY dash-prefixed global (not a curated allow-list):
# a P0 review (2026-07-09) found the prior allow-list omitted the real short
# globals `-p` (= --paginate) and `-P` (= --no-pager), so `git -p push --force`
# / `git -P reset --hard` / `git -p branch -D main` sailed past every git deny.
# The two value-consuming alternatives (`-c`/`-C <val>` and the separate-token
# long globals) MUST stay FIRST so a global's separate-token VALUE is consumed
# with it — POSIX leftmost-longest then prefers them over the general trailing
# alternatives, so `git -c key=val push` folds to `git push` (not `git key=val`).
# The general alternatives (`--flag[=val]` and `-x`) cover -p/-P and any future
# git global. Subcommand options like `-f`/`--force`/`-D` are never in the leading
# run (they follow the subcommand), so they are preserved.
_gitglobal='(-[cC][[:space:]]*[^[:space:]]+|--(git-dir|work-tree|namespace|exec-path|config-env)(=[^[:space:]]*|[[:space:]]+[^[:space:]]+)|--[A-Za-z][A-Za-z-]*(=[^[:space:]]*)?|-[A-Za-z]+)'
_gstripped="$(printf '%s' "$norm" | sed -E "s/(^|[;&|[:space:]])git(([[:space:]]+${_gitglobal})+)[[:space:]]+/\1git /g" 2>/dev/null || true)"
[ -n "$_gstripped" ] && norm="$_gstripped"

# --- Order-independent helpers ---------------------------------------------
# Characters that open a fresh command word before rm/chmod: line start, ;, &, |,
# whitespace, a command-substitution opener — `(` or a backtick — so `$(rm -rf ~)`
# / ``rm -rf ~`` are caught, AND `/` so a path-qualified invocation (`/bin/rm`,
# `./rm`, `../rm`) is caught (the command name need not be the first token).
# Single-quoted so the literal backtick can't trigger command substitution here.
_CMD_BOUNDARY='(^|[;&|(`/[:space:]])'

# Characters that CLOSE a command word: whitespace, end-of-string, or a command-
# substitution closer — `)` or a backtick — so a trailing action inside `$(…)` /
# `` `…` `` (e.g. `$(find / -delete)`) is recognized. Single-quoted so the literal
# backtick can't trigger command substitution here (mirrors _CMD_BOUNDARY).
_CMD_END='([[:space:])`]|$)'

# A recursive flag in ANY spelling/order: -r, -R, -rf, -fr, -Rf, --recursive.
_has_recursive() { [[ "$1" =~ (^|[[:space:]])(-[a-zA-Z]*[rR][a-zA-Z]*|--recursive)([[:space:]]|$) ]]; }

# rm of a dangerous root (/, ~, $HOME — but NOT ./relative) recursively, in any
# flag order. Force is NOT required: a recursive rm of / or $HOME is fatal on
# its own. `rm -rf ./tmp/build` is allowed (target is relative, starts with `.`).
_is_dangerous_rm() {
  local c="$1"
  # _CMD_BOUNDARY covers command-substitution openers ($(/backtick) AND `/` for a
  # path-qualified invocation (`/bin/rm`, `./rm`, `../rm`).
  [[ "$c" =~ ${_CMD_BOUNDARY}rm[[:space:]] ]] || return 1
  _has_recursive "$c" || return 1
  # a dangerous target argument: starts with /, ~, $HOME, or a standalone . or *
  # $HOME is boundary-anchored so `$HOME_BACKUP` / `$HOME_DIR` (a *different*
  # variable) is not falsely matched as a prefix — only bare `$HOME`, `$HOME/…`,
  # `$HOME ` etc. count (ERE has no \b, so require a non-identifier char or EOL).
  [[ "$c" =~ (^|[[:space:]])(/|~|\$HOME([^_[:alnum:]]|$)) ]] && return 0
  # standalone current-dir / parent-dir / glob target. Covers `.`, `./`, `*`
  # (trailing slash is the same current-dir delete) AND the wipe-cwd / escape-to-
  # parent globs `.*`, `./*`, `..`, `../`, `../*` — `../*` is the worst case: it
  # deletes the ENTIRE PARENT directory, escaping the cwd-container blast-radius
  # bound this function's design (above) relies on to allow relative deletes.
  # Scoped relative paths (`./tmp/build`, `../build`) still fall through (allowed):
  # they carry a non-`*` path segment after the dots, so the boundary anchor fails.
  [[ "$c" =~ (^|[[:space:]])(\.{1,2}/?\*?|\*)([[:space:]]|$) ]] && return 0
  return 1
}

# chmod recursively to a world-writable / lockout octal mode (777/666/000), in
# any flag order, octal prefix tolerated (0777). Symbolic modes are out of scope.
_is_dangerous_chmod() {
  local c="$1"
  # _CMD_BOUNDARY also covers path-qualified `/usr/bin/chmod` (see _is_dangerous_rm).
  [[ "$c" =~ ${_CMD_BOUNDARY}chmod[[:space:]] ]] || return 1
  _has_recursive "$c" || return 1
  [[ "$c" =~ (^|[[:space:]])0?(7{3}|6{3}|0{3})([[:space:]]|$) ]] || return 1
  return 0
}

# `find` with a destructive action (-delete, or -exec rm/unlink/shred/truncate)
# AIMED at a dangerous ABSOLUTE root: an absolute path (/, /etc, …), ~, or $HOME
# (e.g. `find / -delete`, `find $HOME -exec rm {} +`). `find -delete` is a
# well-known mass-delete idiom (the runaway-brake's read-only carve-out already
# excludes `find` for this very reason). Scope is deliberately the absolute/HOME
# root ONLY — a relative target (`find . -name '*.tmp' -delete`,
# `find ./build -delete`) is an extremely common, legitimate cleanup idiom and is
# ALLOWED; the bare-cwd `find . -delete` wipe is the one residual gap accepted to
# avoid false-positiving the common filtered form (the cwd container is the
# blast-radius bound for that one, same as the worktree/sandbox posture).
_is_dangerous_find() {
  local c="$1"
  # _CMD_BOUNDARY covers command-substitution openers ($(/backtick) AND `/` for a
  # path-qualified invocation (`/usr/bin/find`) — the narrower `[;&|space/]` class
  # let `$(find / -delete)` slip past while `$(rm -rf ~)` was caught (2026-07 review).
  [[ "$c" =~ ${_CMD_BOUNDARY}find[[:space:]] ]] || return 1
  # a destructive action must be present. `-execdir` is the functional twin of
  # `-exec` (runs the command per-match) — match both spellings.
  [[ "$c" =~ (^|[[:space:]])-delete${_CMD_END} ]] \
    || [[ "$c" =~ -exec(dir)?[[:space:]]+(sudo[[:space:]]+)?(rm|unlink|shred|truncate)([[:space:]]|$) ]] \
    || return 1
  # dangerous target: absolute path / ~ / $HOME
  [[ "$c" =~ (^|[[:space:]])(/|~|\$HOME) ]] && return 0
  return 1
}

# `truncate -s 0` (empty-the-file) of a dangerous root — an absolute path, ~, or
# $HOME (e.g. `truncate -s 0 /etc/passwd`). Size 0 in any spelling (-s0 / -s 0 /
# -s 0K). A relative target (`truncate -s 0 ./app.log`) is ALLOWED — same
# dangerous-root philosophy as rm/find.
_is_dangerous_truncate() {
  local c="$1"
  # _CMD_BOUNDARY covers command-substitution openers ($(/backtick) AND `/` for a
  # path-qualified invocation — see _is_dangerous_find (2026-07 review boundary gap).
  [[ "$c" =~ ${_CMD_BOUNDARY}truncate[[:space:]] ]] || return 1
  # size 0 in any spelling: -s0 / -s 0 / -s 0K AND the long option --size=0 / --size 0.
  [[ "$c" =~ (-s[[:space:]]*|--size[[:space:]]*=?[[:space:]]*)0([[:space:]]|$|[bkKMGT]) ]] || return 1
  [[ "$c" =~ (^|[[:space:]])(/|~|\$HOME) ]] && return 0
  return 1
}

# Force-delete of a git branch, order-independent (added after the 2026-07 review).
# The prior single pattern anchored `-D` immediately after `branch`, so it caught
# `git branch -D main` / `-fD` / `-Df` but MISSED the long form
# `git branch --delete --force main` (and `--force --delete`) and the reordered
# `git branch main -D`. Scan the whole `git branch …` invocation for either the
# short force-delete flag (contains an uppercase D) OR the co-occurrence of
# `--delete` and `--force` anywhere. (git global options are already stripped above.)
_is_dangerous_git_branch_delete() {
  local c="$1"
  # _CMD_BOUNDARY covers command-substitution openers ($(/backtick) — the narrower
  # class let `$(git branch -D main)` slip past (2026-07 review boundary gap).
  [[ "$c" =~ ${_CMD_BOUNDARY}git[[:space:]]+branch([[:space:]]|$) ]] || return 1
  # short combined flag containing D:  -D / -fD / -Df
  [[ "$c" =~ (^|[[:space:]])-[a-zA-Z]*D[a-zA-Z]*([[:space:]]|$) ]] && return 0
  # long form: both --delete and --force present, in any order
  { [[ "$c" =~ (^|[[:space:]])--delete([[:space:]]|$) ]] && [[ "$c" =~ (^|[[:space:]])--force([[:space:]]|$) ]]; } && return 0
  return 1
}

# --- Pattern array (matched against the normalized command) ----------------
# The settings.json deny-list catches the top-level form; this catches them
# when nested / wrapped / reordered.
deny_patterns=(
  # git history / branch destruction
  'git[[:space:]]+push[[:space:]]+.*--force([[:space:]]|$)'        # --force (allows --force-with-lease)
  'git[[:space:]]+push[[:space:]]+(.*[[:space:]])?-[A-Za-z]*f[A-Za-z]*([[:space:]]|$)'  # -f in ANY bundled short-flag cluster (git push -uf), order-independent like _has_recursive; does NOT match --force-with-lease
  'git[[:space:]]+push[[:space:]].*[[:space:]]\+[A-Za-z0-9_./@~^-]+'  # refspec force-push: git push origin +HEAD:main
  'git[[:space:]]+reset[[:space:]]+--hard([[:space:]]+|$)'
  'git[[:space:]]+clean[[:space:]]+(-[a-z]*f|--force)'             # clean -fd / -df / --force (order-independent)
  # NB: git force-branch-delete is handled by _is_dangerous_git_branch_delete
  # (order-independent, incl. the `--delete --force` long form), not a pattern.
  # remote-code-exec via pipe / process- or command-substitution to an interpreter
  '(curl|wget)[^|]*\|[[:space:]]*(sudo[[:space:]]+)?(env[[:space:]]+[^[:space:]]+[[:space:]]+)?([a-z]*sh|python[0-9.]*|perl|ruby|node)([[:space:]]|$)'
  # …and the multi-pipe / filter-then-execute evasion of the above: the single-pipe
  # form only inspects between curl/wget and the FIRST pipe, so `curl … | tee x | bash`
  # or `curl … | grep -v '#' | sh` slipped past. This catches an interpreter that is
  # the IMMEDIATE target of ANY pipe in a curl/wget chain (the interpreter right after
  # a `|`), so `… | grep python` is NOT matched (grep, not python, is the pipe target).
  '(curl|wget).*\|[[:space:]]*(sudo[[:space:]]+)?(env[[:space:]]+[^[:space:]]+[[:space:]]+)?([a-z]*sh|python[0-9.]*|perl|ruby|node)([[:space:]]|$)'
  '<\([[:space:]]*(curl|wget)'                                    # bash <(curl …)
  '\$\([[:space:]]*(curl|wget)'                                   # sh -c "$(curl …)" (quotes stripped by norm)
  # whole-disk / filesystem destruction
  'dd[[:space:]]+.*of=/dev/(sd|nvme|hd|disk|vd|xvd|mmcblk|loop)'
  '(^|[[:space:]])mkfs([.[:space:]]|$)'
  '(^|[[:space:]])wipefs([[:space:]]|$)'
  'shred[[:space:]]+.*[[:space:]]/dev/'
  '>[[:space:]]*/dev/(sd|nvme|hd|disk|vd|xvd|mmcblk)'
  # fork bomb
  ':[[:space:]]*\([[:space:]]*\)[[:space:]]*\{[[:space:]]*:\|:&[[:space:]]*\}'
)

_deny() {
  local reason="$1"
  _emit_hook_event "guard-destructive.sh" "deny" "Bash" "$cmd" "$reason" 2
  # Scrub secret-shaped tokens before echoing the command to stderr — the stderr
  # of a blocked tool call is captured into the conversation transcript, so a
  # credential embedded in a destructive command would otherwise leak there
  # (the JSONL substrate is already scrubbed inside _emit_hook_event above).
  local safe_cmd safe_reason
  safe_cmd="$(_scrub_reason "$cmd" 2>/dev/null || printf '%s' "$cmd")"
  safe_reason="$(_scrub_reason "$reason" 2>/dev/null || printf '%s' "$reason")"
  echo "[guard-destructive] BLOCKED: command matches destructive pattern: $safe_reason" >&2
  echo "[guard-destructive] cmd: $safe_cmd" >&2
  echo "[guard-destructive] If you really need this, run it yourself with explicit confirmation." >&2
  exit 2   # 2 blocks the tool call; 1 would NOT (non-blocking error)
}

# Order-independent structural checks first.
if _is_dangerous_rm "$norm";       then _deny "recursive-rm-of-dangerous-target"; fi
if _is_dangerous_chmod "$norm";    then _deny "recursive-chmod-world-or-lockout"; fi
if _is_dangerous_find "$norm";     then _deny "find-delete-of-dangerous-target"; fi
if _is_dangerous_truncate "$norm"; then _deny "truncate-zero-of-dangerous-target"; fi
if _is_dangerous_git_branch_delete "$norm"; then _deny "git-branch-force-delete"; fi

# Then the pattern array.
for pat in "${deny_patterns[@]}"; do
  if [[ "$norm" =~ $pat ]]; then _deny "$pat"; fi
done

exit 0
