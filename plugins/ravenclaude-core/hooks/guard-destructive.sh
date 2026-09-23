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
# Initialize before the python3 block so the `[ -n "$__preproc" ]` consume below is
# always DEFINED under `set -u` (an absent python3 skips the assignment; an unbound
# read would abort the guard with a non-2 exit -> non-blocking -> command UNCHECKED).
__preproc=""
if command -v python3 >/dev/null 2>&1; then
  # Load the preprocessor into a variable via a here-doc fed to `read` -- a SIMPLE
  # command, NOT nested in $(). macOS's stock bash 3.2 mis-parses a here-doc nested
  # inside $(...) and starts reading the Python below as shell (syntax error -> exit
  # 2 -> every Bash command wrongly blocked); a here-doc to `read` parses on every
  # bash. Then run it with `python3 -c` (NO temp file), so the decoder has no
  # filesystem dependency and runs whenever python3 exists -- this closes the fail-
  # OPEN where a failed mktemp/cat would silently drop the ANSI-C ($'...') anti-
  # obfuscation layer and let an obfuscated destructive command through. `read -d ''`
  # returns non-zero at EOF (no NUL) but still assigns; `|| :` keeps that from
  # tripping `set -e`. The command under inspection travels via the __GUARD_RAW_CMD
  # env var, never through this program text.
  IFS= read -r -d '' __GUARD_PY <<'PY' || :
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
  # exit from the `python3 -c` call (e.g. an exotic UnicodeEncodeError) would trip
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
# Round 4 (2026-09-23, Bugbot): this stripping step is exactly why a
# `-C <dir>`/`--git-dir=<dir>` on a `git merge` invocation used to bypass
# _is_dangerous_merge's HEAD-branch check entirely — by the time `norm`
# reached that function, the -C/--git-dir flag (and the dir it named) was
# already gone, folded away into a bare "git merge". Keep the PRE-strip
# text around so _is_dangerous_merge can still see which directory the
# merge actually targets.
_norm_before_gitstrip="$norm"
_gstripped="$(printf '%s' "$norm" | sed -E "s/(^|[;&|[:space:]])git(([[:space:]]+${_gitglobal})+)[[:space:]]+/\1git /g" 2>/dev/null || true)"
[ -n "$_gstripped" ] && norm="$_gstripped"

# Round 5 (2026-09-23, Bugbot): mirror the git-global fold above for the
# GitHub CLI's own global options (`-R owner/repo`, `--repo owner/repo`,
# `--hostname host`, …) sitting between `gh` and its subcommand. Without
# this, `gh -R owner/repo api ... -X DELETE` / `gh --repo owner/repo api
# ... --method DELETE` / `gh --hostname github.com api ... -X DELETE`
# dodge the `gh[[:space:]]+api` anchor in the destructive-DELETE
# deny_patterns entry below, exactly like the git-global gap this same
# stripper closed for git subcommands.
_ghglobal='(-R[[:space:]]*[^[:space:]]+|--(repo|hostname)(=[^[:space:]]*|[[:space:]]+[^[:space:]]+)|--[A-Za-z][A-Za-z-]*(=[^[:space:]]*)?|-[A-Za-z]+)'
_ghstripped="$(printf '%s' "$norm" | sed -E "s/(^|[;&|[:space:]])gh(([[:space:]]+${_ghglobal})+)[[:space:]]+/\1gh /g" 2>/dev/null || true)"
[ -n "$_ghstripped" ] && norm="$_ghstripped"

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
  # `(\.{1,2}/?)+` matches ONE OR MORE dot/dot-dot navigation segments, so multi-hop
  # escapes (`../../`, `../../*`, `../../../`) are caught, not just a single `../`.
  # A single-segment form (`.`, `..`, `./`, `../`, `.*`, `./*`, `../*`) is the `+`=1
  # case, so prior coverage is preserved. Scoped relative paths (`./tmp/build`,
  # `../build`) still fall through — a non-dot path segment breaks the trailing anchor.
  [[ "$c" =~ (^|[[:space:]])((\.{1,2}/?)+\*?|\*)([[:space:]]|$) ]] && return 0
  return 1
}

# chmod recursively to a world-writable / lockout octal mode (777/666/000), in
# any flag order, octal prefix tolerated (0777). Symbolic modes are out of scope.
_is_dangerous_chmod() {
  local c="$1"
  # _CMD_BOUNDARY also covers path-qualified `/usr/bin/chmod` (see _is_dangerous_rm).
  [[ "$c" =~ ${_CMD_BOUNDARY}chmod[[:space:]] ]] || return 1
  _has_recursive "$c" || return 1
  # A leading special-permission digit `[0-7]?` (not just `0?`) so setuid/setgid/
  # sticky forms — `chmod -R 4777`/`2777`/`6777`/`1777` (world-writable PLUS an
  # elevated-privilege bit, strictly WORSE than a plain 777) — are caught, not only
  # the plain-octal `0777` prefix. Benign modes (644/755/…) still don't match.
  [[ "$c" =~ (^|[[:space:]])[0-7]?(7{3}|6{3}|0{3})([[:space:]]|$) ]] || return 1
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

# Remote branch deletion via `git push` (added after the 2026-08 review). The
# deny_patterns git-push rules only cover FORCE-push (--force / -f / +refspec);
# they miss OUTRIGHT remote-branch DELETION, which is equally destructive
# (deleting a remote branch — including an unprotected main/master — is
# unrecoverable outside someone's local clone/reflog). Two forms, neither of
# which contains --force/-f/+ nor the literal `branch` subcommand, so no existing
# rule matches: the flag form `git push <remote> --delete <ref>` / `-d` (any
# order), and the colon-refspec form `git push <remote> :<ref>` (empty source
# side = delete). Mirrors _is_dangerous_git_branch_delete's order-independent
# shape. The sanctioned escape hatch for a genuinely-needed remote delete is the
# same as for local branch delete: scripts/archive-branch.sh / cleanup-branches.sh
# (their internal push runs as a subprocess, which this PreToolUse hook does not
# intercept), or GitHub's own delete-branch UI.
_is_dangerous_git_push_delete() {
  local c="$1" seg found=1
  [[ "$c" =~ ${_CMD_BOUNDARY}git[[:space:]]+push([[:space:]]|$) ]] || return 1

  # ⛔ THE FLAG SEARCH IS SCOPED TO THE `git push` SEGMENT. It used to run over
  # the WHOLE command string, so a `-d` belonging to an entirely different
  # command in the same line was read as `git push --delete`.
  #
  # control (2026-08-18): `git push -u origin b; echo $(wc -w | tr -d ' ')`
  # -> DENIED as git-push-remote-branch-delete. Nothing is deleted there; the
  # `-d` is `tr`'s. The same command with the `tr` removed -> allowed, so the
  # trigger was the unrelated token, not the push.
  #
  # The header comment claimed "-d is the ONLY push short flag containing a
  # lowercase d", which is true of `git push` and irrelevant: the regex was
  # never looking only at `git push`. This is the third instance of that class
  # in this file's family (srm.force-push v0.242.0, sce.curl-pipe-shell
  # v0.244.0) — when a rule matches on a token, scope it to the command that
  # token belongs to.
  #
  # Splitting on ; & | is correct HERE because a push flag never crosses a
  # separator. (curl-pipe-shell deliberately does NOT exclude `|` — same defect
  # class, opposite correct remedy, because a fetch piped into a shell is the
  # very thing it hunts.)
  while IFS= read -r seg; do
    case "$seg" in *"git push"*) ;; *) continue ;; esac
    # long delete flag
    [[ "$seg" =~ (^|[[:space:]])--delete([[:space:]]|$) ]] && { found=0; break; }
    # short delete flag `-d`, standalone or bundled
    [[ "$seg" =~ (^|[[:space:]])-[a-zA-Z]*d[a-zA-Z]*([[:space:]]|$) ]] && { found=0; break; }
    # colon-refspec deletion: a refspec whose SOURCE side is empty (`:<ref>`). A
    # normal refspec `src:dst` has no space before the colon, so requiring a
    # space immediately before `:` matches only the deletion form and never
    # `main:main` / `HEAD:refs/heads/main`.
    [[ "$seg" =~ [[:space:]]:[A-Za-z0-9_./@^~*-]+([[:space:]]|$) ]] && { found=0; break; }
  done <<EOF
$(printf '%s' "$c" | tr ';&|' '\n\n\n')
EOF
  return $found
}

# `git clean` force, order-independent (added after the 2026-08 review). The
# prior single pattern `git[[:space:]]+clean[[:space:]]+(-[a-z]*f|--force)`
# anchored the force flag IMMEDIATELY after `clean`, so it caught the bundled
# `git clean -df` but MISSED the separated-token idiom `git clean -d -f` /
# `git clean -x -f .` (force flag preceded by another flag). Scan the whole
# invocation for a force flag anywhere, mirroring _has_recursive. `git clean`
# is a no-op without a force flag, so any force flag = a real untracked-file
# wipe (deletes files git never tracked — no history recovery).
_is_dangerous_git_clean() {
  local c="$1"
  [[ "$c" =~ ${_CMD_BOUNDARY}git[[:space:]]+clean([[:space:]]|$) ]] || return 1
  # -f in ANY bundled short-flag cluster (-f / -fd / -df / -xf), any position
  [[ "$c" =~ (^|[[:space:]])-[a-zA-Z]*f[a-zA-Z]*([[:space:]]|$) ]] && return 0
  [[ "$c" =~ (^|[[:space:]])--force([[:space:]]|$) ]] && return 0
  return 1
}

# Bypass-shaped merge only — added for source-control-coordinator (build-plan.md
# Task 3.3). Deliberately NARROW: it does NOT deny an ordinary merge with no
# bypass flag (e.g. `gh pr merge <n> --squash`) — a blanket "any merge to a
# protected branch" pattern would disable the coordinator's own sanctioned
# invocation via the hook this plan calls the least-privilege bound, which is
# its entire reason for existing. Whether a *particular* sanctioned call is
# *safe to make right now* is the coordinator's own authoritative pre-merge
# check's job (source-control-coordinator.md), not this hook's.
#
# Two bypass shapes, both order-independent:
#   (a) `gh pr merge` carrying an admin-override flag (`--admin`), in any flag
#       order — both `gh pr merge <n> --admin --squash` and
#       `gh pr merge <n> --squash --admin` must match.
#   (b) a LOCAL `git merge` while checked out on a protected branch (main/
#       master) without `--ff-only` — capable of landing a real merge commit
#       directly on that branch, bypassing PR review entirely. `--ff-only` is
#       explicitly exempted: a pure fast-forward changes no history shape and
#       is not the bypass this rule targets.
#
# ⛔ Eight review findings folded in across five Bugbot passes (all real,
# none hypothetical — each pass reviewed the PRIOR pass's fix and found
# genuine regressions or gaps in it):
#   - (round 1) The `--ff-only` exemption is checked ONLY within the `git
#     merge` segment, mirroring how the `--admin` check above it is already
#     scoped per segment — an unscoped check against the WHOLE command
#     string would let a `--ff-only` token anywhere else in a compound
#     command falsely exempt a real merge-commit-shaped bypass.
#   - (round 1) The effective branch is tracked ACROSS segments, not read
#     once from current HEAD before the command runs — `git checkout main
#     && git merge feature --no-ff` changes HEAD mid-command, so reading it
#     once at hook-eval time sees the PRE-checkout branch and misses the
#     bypass entirely.
#   - (round 2) EVERY `git merge` segment is evaluated in order, never
#     stopping at the first — the round-1 fix matched the substring "git
#     merge" and broke on the first hit, which also fires on `git merge-base`
#     and `git mergetool` (neither actually merges), so a command opening
#     with either before the real merge would have stopped the scan too
#     early. The merge check is now a proper word-boundary match ("git
#     merge" followed by whitespace/EOL, never "-base"/"tool") and the loop
#     never breaks — it denies on the FIRST segment that is genuinely
#     dangerous, wherever it falls.
#   - (round 3) The checkout/switch parser distinguishes the CREATED branch
#     from a start-point operand — `git checkout -b newbranch main` (or
#     `git switch -c feature main`) ends up ON `newbranch`/`feature`, NOT on
#     `main`; a round-2 "last leftover word wins" heuristic would have
#     tracked "main" instead, since it's the LAST word in the segment. The
#     parser now special-cases `-b`/`-B`/`-c`/`--orphan`: the word
#     IMMEDIATELY FOLLOWING one of those flags is the target, taking
#     priority over any other operand in the segment. Absent one of those
#     flags, the target is the FIRST non-flag word after `checkout`/`switch`
#     (not the last) — which also closes a related round-2 gap: a trailing
#     redirect or comment after the real branch name (`git checkout main
#     2>/dev/null`) no longer overwrites a correctly-tracked branch, since
#     only the FIRST positional word is taken, not whatever comes last.
#   - (round 3) Every per-segment structural check (the merge/checkout-
#     switch word-boundary tests) now reuses `${_CMD_BOUNDARY}` — the SAME
#     boundary-character class the outer two gates and the `--admin` check
#     already use — instead of a separately hardcoded `(^|[[:space:]])`.
#     Whatever `_CMD_BOUNDARY` recognizes as a command-start boundary
#     (parens, backticks, `;`/`&`/`|`, …) the per-segment checks now
#     recognize too, so a path-qualified or command-substitution-embedded
#     `git merge`/`checkout` that the outer gate can see is never silently
#     invisible to the segment-level checks one level in.
#   - (round 4) The checkout/switch word scan now IGNORES any token BEFORE
#     the actual `git checkout`/`git switch` keyword pair, not just the
#     whole segment naively. A leading redirect (`2>/dev/null git checkout
#     main`), an inline env-var assignment (`FOO=bar git checkout main`), a
#     command wrapper (`sudo git checkout main`) — all valid, realistic bash
#     — were mistaken for the branch by a round-3 loop that took the FIRST
#     non-flag word anywhere in the segment. Isolating everything after the
#     keyword closes the whole class at once rather than chasing prefixes
#     one at a time.
#   - (round 5) The keyword itself is located by exact WORD equality across
#     adjacent tokens (the previous word is literally "git" AND the current
#     word is literally "checkout"/"switch"), not by a substring search. A
#     round-4 draft used `${seg#*"$kw"}` — bash string-prefix removal on the
#     literal text "checkout"/"switch" — which strips at the FIRST substring
#     occurrence, coincidental or not. A prefix token whose own VALUE
#     happens to contain that substring (`FOO=checkout git checkout main`)
#     would have been stripped at the WRONG, earlier occurrence, leaving the
#     real keyword and branch still inside the scanned "tail" — undoing the
#     round-4 fix for that specific shape. Exact per-token equality across
#     ADJACENT words (via ordinary word-splitting, which already respects
#     token boundaries) cannot be fooled by a substring landing inside a
#     single compound token, since `FOO=checkout` is one word, never equal
#     to the bare word `checkout`.
# Round 3 (2026-09-23, Bugbot): the checkout/switch/symbolic-ref word-scan
# used to accept ANY captured token as the new branch name, including one
# glued to a shell redirect (`git checkout main>/dev/null` — the shell
# splits this into the arg "main" plus a redirection, but our plain
# whitespace-based `for word in $seg` sees "main>/dev/null" as ONE word)
# or a command substitution (`git checkout $(true)` — the real branch is
# whatever $(true) evaluates to, which we cannot know). Either shape let
# the tracker "leave" main/master without actually knowing where HEAD
# ended up, silently clearing the deny. Only accept a token that looks
# like a literal git ref (letters/digits/`._/-`, no shell metacharacters)
# as an override; anything else is left alone, keeping the more
# conservative prior value of $branch rather than trusting an ambiguous
# token — under-blocking is the worse failure here, so ambiguity must
# never CLEAR a suspected-main baseline.
_is_safe_ref_token() {
  [[ "$1" =~ ^[A-Za-z0-9._/-]+$ ]]
}

# Round 4 (2026-09-23, Bugbot): an ambiguous checkout/switch/symbolic-ref
# target (one that fails _is_safe_ref_token — a redirect-glued token our
# plain whitespace split didn't fully separate, or a command-substitution
# form we cannot statically resolve) used to just leave the PRIOR $branch
# value in place, on the theory that under-blocking never should trust an
# unresolvable token as an override. That correctly stops an ambiguous
# token from CLEARING a suspected-main baseline (round 3) — but it also
# means an ambiguous token can never SET a genuinely-main target either:
# `git checkout $(echo main)` off a non-main HEAD left $branch at the
# non-main value and silently allowed the following merge. This file's own
# posture on constructs it cannot fully inspect (already applied to
# `--stdin` in _is_dangerous_update_ref above) is to treat the unresolvable
# case as conservatively AS DANGEROUS AS the thing it might be — so an
# ambiguous target sets this sentinel instead, which the final branch
# comparison below treats exactly like main/master.
_AMBIGUOUS_BRANCH_SENTINEL='__ravenclaude_ambiguous_branch__'

# Round 4 (2026-09-23, Bugbot): the merge-detection regexes required the
# literal contiguous substring "git merge" (git, whitespace, merge, nothing
# else in between) — so `git -C /other/repo merge --no-ff feature` or
# `git --git-dir=/other/repo/.git merge feature` never matched AT ALL (not
# even the outer gate), because git's own global `-C`/`--git-dir` options
# sit between the "git" token and the "merge" subcommand. This fragment
# tolerates zero-or-more such global options in between, on both the outer
# whole-command gate and the per-segment scan below.
_GIT_MERGE_GLOBAL_OPTS='((-C|--git-dir)[[:space:]=]+[^[:space:]]+[[:space:]]+)*'

# Round 4 (2026-09-23, Bugbot): `_is_dangerous_merge` computed the "current
# branch" exactly ONCE, from the hook process's own cwd, and never revisited
# it for (a) a `-C <dir>`/`--git-dir=<dir>` flag on the `git merge`
# invocation ITSELF, which targets a wholly different repo than the hook's
# cwd, or (b) a preceding `cd <dir> &&` segment in the same command chain
# redirecting into a different repo entirely. Either shape let a merge into
# another repo's main/master sail through using the WRONG repo's branch
# name. Given a merge segment and the tracked $effective_cwd (updated by
# `cd` segments seen so far), resolve the real branch to check: a -C/
# --git-dir flag on THIS segment wins outright (most specific); otherwise
# fall back to $effective_cwd if a prior `cd` set one; otherwise print
# nothing so the caller keeps using the textually-tracked $branch (the
# pre-existing, same-repo behavior — unchanged when neither applies).
#
# Round 5 (2026-09-23, Bugbot): the round-4 fix followed -C/--git-dir FLAGS
# and a `cd` chain, but git also honors the GIT_DIR environment variable —
# either as a one-shot prefix on the SAME command (`GIT_DIR=<dir> git
# merge …`) or exported earlier in the chain (`export GIT_DIR=<dir>; git
# merge …`) — and neither was tracked, so retargeting through the
# environment instead of a flag sailed through. `gitdir_override` carries
# a persistent GIT_DIR set earlier in the same chain (mirrors
# $effective_cwd for `cd`/`pushd`); the same-segment `GIT_DIR=<dir>` prefix
# is checked first here since it is the most specific (a one-shot prefix
# overrides any exported value for that single invocation, matching real
# shell semantics).
_resolve_merge_check_branch() {
  local seg="$1" fallback_dir="$2" gitdir_override="$3" word prev="" dir="" mode=""
  for word in $seg; do
    case "$word" in
      GIT_DIR=*) dir="${word#GIT_DIR=}"; mode="--git-dir" ;;
    esac
    [ -n "$dir" ] && break
    case "$prev" in
      -C) dir="$word"; mode="-C" ;;
      --git-dir) dir="$word"; mode="--git-dir" ;;
    esac
    [ -n "$dir" ] && break
    case "$word" in
      --git-dir=*) dir="${word#--git-dir=}"; mode="--git-dir" ;;
    esac
    [ -n "$dir" ] && break
    prev="$word"
  done
  if [ -z "$dir" ] && [ -n "$gitdir_override" ]; then
    dir="$gitdir_override"; mode="--git-dir"
  fi
  if [ -z "$dir" ] && [ -n "$fallback_dir" ]; then
    dir="$fallback_dir"; mode="-C"
  fi
  [ -z "$dir" ] && return 1
  if [ "$mode" = "--git-dir" ]; then
    git --git-dir="$dir" rev-parse --abbrev-ref HEAD 2>/dev/null || true
  else
    git -C "$dir" rev-parse --abbrev-ref HEAD 2>/dev/null || true
  fi
}

_is_dangerous_merge() {
  local c="$1" raw="${2:-$1}" seg found=1
  # ⛔ Bugbot review (2026-09-22, PR #1241): the original gate required the
  # literal contiguous substring "gh pr merge" and closed --admin with
  # ([[:space:]]|$), so it missed EVERY realistic real-world spelling: gh
  # global flags between the subcommand and `pr` (`gh -R owner/repo pr merge`,
  # `gh --repo owner/repo pr merge`), a command-substitution wrapper
  # (`$(gh pr merge 1 --admin)` — the string does not END right after
  # `--admin`, `)` does), and `--admin=true`. Fixed by (a) testing for `gh`,
  # `pr`, `merge`, and `--admin` as four independent boundary-anchored WORDS
  # in the same segment — order- and adjacency-independent, so gh globals in
  # between cannot hide the pattern — and (b) using `_CMD_END` (which already
  # covers `)`/backtick/space/EOL) plus an optional `=value` tail for the
  # admin flag itself. Looser word-presence matching can in principle flag a
  # segment that merely MENTIONS all four words (e.g. explaining this fix in
  # a commit message run through the same Bash call) — the same accepted
  # prose-vs-command tradeoff this file already makes for the force-push and
  # curl-pipe-shell hard rules; under-blocking a real bypass is the worse
  # failure for a `pre_llm_deny`-adjacent security floor.
  if [[ "$c" =~ ${_CMD_BOUNDARY}gh([[:space:]]|$) ]]; then
    while IFS= read -r seg; do
      [[ "$seg" =~ ${_CMD_BOUNDARY}gh([[:space:]]|$) ]] || continue
      [[ "$seg" =~ ${_CMD_BOUNDARY}pr([[:space:]]|$) ]] || continue
      [[ "$seg" =~ ${_CMD_BOUNDARY}merge([[:space:]]|$) ]] || continue
      [[ "$seg" =~ ${_CMD_BOUNDARY}--admin(=[^[:space:]]*)?${_CMD_END} ]] && { found=0; break; }
    done <<EOF
$(printf '%s' "$c" | tr ';&|' '\n\n\n')
EOF
    [ "$found" -eq 0 ] && return 0
  fi
  if [[ "$c" =~ ${_CMD_BOUNDARY}git[[:space:]]+${_GIT_MERGE_GLOBAL_OPTS}merge([[:space:]]|$) ]]; then
    local branch word prev seen seg_target pending pending_kind double_dash first_pos symref_target
    local effective_cwd="" cd_word cd_prev cd_seen cd_target gd_word
    # Round 5 (2026-09-23, Bugbot): a persistent GIT_DIR set earlier in the
    # same chain (`export GIT_DIR=<dir>; git merge …`) retargets every
    # subsequent git invocation exactly like `cd` does for the working
    # directory — tracked separately since GIT_DIR is a `--git-dir`-shaped
    # override, not a `-C`-shaped one.
    local effective_gitdir=""
    branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
    # Round 4 (2026-09-23, Bugbot): the earlier `git[[:space:]]+global-option
    # strip` normalization (applied to `$norm` before this function ever
    # sees it) folds a `-C <dir>`/`--git-dir=<dir>` on a `git merge`
    # invocation away entirely, so `$seg` (derived from `$c` == the
    # STRIPPED command) can no longer see which directory that merge
    # targets. `$raw` is the PRE-strip text passed in by the caller;
    # split it into an index-aligned segment array so the merge check
    # below can look at the unstripped `raw_seg` for the -C/--git-dir
    # flag while everything else keeps using the stripped `seg`.
    local -a _raw_segs=()
    local _rseg _idx=0
    while IFS= read -r _rseg; do
      _raw_segs+=("$_rseg")
    done <<EOF
$(printf '%s' "$raw" | tr ';&|' '\n\n\n')
EOF
    while IFS= read -r seg; do
      local raw_seg="${_raw_segs[_idx]:-$seg}"
      _idx=$((_idx + 1))
      # Round 4 (2026-09-23, Bugbot): `cd <dir> && git merge ...` targets a
      # DIFFERENT repo than the one the hook process's own cwd sits in — the
      # $branch computed above (from the hook's cwd) is then simply wrong
      # for the merge that follows. Track the effective directory across
      # `cd` segments so a later `git merge` in the same chain can re-resolve
      # HEAD from the right place (see _resolve_merge_check_branch below).
      # Round 5 (2026-09-23, Bugbot): `pushd <dir>` retargets the working
      # directory for every subsequent command in the chain exactly like
      # `cd <dir>` does (we don't track `popd`'s later restoration —
      # staying pinned to the pushd'd directory is the conservative,
      # under-blocking-never direction for a security floor).
      if [[ "$seg" =~ ${_CMD_BOUNDARY}(cd|pushd)([[:space:]]|$) ]]; then
        cd_prev="" cd_seen="" cd_target=""
        for cd_word in $seg; do
          if [ -z "$cd_seen" ]; then
            { [ "$cd_word" = "cd" ] || [ "$cd_word" = "pushd" ]; } && cd_seen=1
            cd_prev="$cd_word"
            continue
          fi
          case "$cd_word" in
            -*) ;;
            *) [ -z "$cd_target" ] && cd_target="$cd_word" ;;
          esac
        done
        if [ -n "$cd_target" ] && [[ "$cd_target" =~ ^[A-Za-z0-9._/~+-]+$ ]]; then
          case "$cd_target" in
            /*) effective_cwd="$cd_target" ;;
            *) [ -n "$effective_cwd" ] && effective_cwd="$effective_cwd/$cd_target" || effective_cwd="$cd_target" ;;
          esac
        fi
      fi
      # Round 5 (2026-09-23, Bugbot): git also honors the GIT_DIR
      # environment variable, which can be set persistently earlier in the
      # same command chain (`export GIT_DIR=<dir>; git merge …`, or a bare
      # `GIT_DIR=<dir>` — real shell semantics require `export` for a LATER
      # separate command to see it, but a security floor treats the
      # ambiguous unexported form as dangerous too, matching this file's
      # posture elsewhere). Only a single assignment token is recognized
      # (no quoting/expansion), matching the same-scope limits already
      # accepted for `cd`/`pushd` target parsing above.
      if [[ "$seg" =~ ${_CMD_BOUNDARY}(export[[:space:]]+)?GIT_DIR= ]]; then
        gd_word=""
        for gd_word in $seg; do
          case "$gd_word" in
            GIT_DIR=*)
              # A same-segment prefix directly preceding a git invocation
              # (`GIT_DIR=<dir> git merge …`) is a ONE-SHOT override for
              # that command only — handled by _resolve_merge_check_branch
              # itself (it re-scans the segment), not here. Only persist a
              # standalone assignment/export (no git command in the SAME
              # segment) as the running override for later segments.
              if [[ ! "$seg" =~ ${_CMD_BOUNDARY}git([[:space:]]|$) ]]; then
                effective_gitdir="${gd_word#GIT_DIR=}"
              fi
              ;;
          esac
        done
      fi
      if [[ "$seg" =~ ${_CMD_BOUNDARY}git[[:space:]]+(checkout|switch)([[:space:]]|$) ]]; then
        prev="" seen="" seg_target="" pending="" pending_kind="" double_dash="" first_pos=""
        # Round 4 (2026-09-23, Bugbot): a redirect glued directly onto the
        # target with no whitespace (`git checkout main>/dev/null`) reads
        # as ONE word under a plain `for word in $seg` split, so the target
        # extraction below never saw "main" in isolation. Insert whitespace
        # around `<`/`>` first so the split sees them as separate tokens —
        # this only ever ADDS a word boundary, it cannot merge two tokens
        # that were already separate.
        local seg_split="${seg//>/ > }"
        seg_split="${seg_split//</ < }"
        for word in $seg_split; do
          if [ -z "$seen" ]; then
            if [ "$prev" = "git" ] && { [ "$word" = "checkout" ] || [ "$word" = "switch" ]; }; then
              seen=1
            fi
            prev="$word"
            continue
          fi
          if [ -n "$pending" ]; then
            if [ "$pending_kind" = "track" ]; then
              # Round 2 (2026-09-22, Bugbot): `git checkout -t origin/main`
              # (or `switch -t`) creates a LOCAL branch named after the
              # remote-tracking ref's own name (stripping the leading
              # "<remote>/"), not a branch literally called "origin/main" —
              # so the bare main|master case arm below never matched. Strip
              # up to the first "/" the same way a real -t/--track resolves
              # the local branch name.
              seg_target="${word#*/}"
            else
              seg_target="$word"
            fi
            pending=""; pending_kind=""; continue
          fi
          case "$word" in
            --) double_dash=1; break ;;
            -b|-B|-c|--orphan) pending=1; pending_kind="name" ;;
            -t|--track) pending=1; pending_kind="track" ;;
            -*) ;;
            *) [ -z "$first_pos" ] && first_pos="$word" ;;
          esac
        done
        if [ -n "$seg_target" ]; then
          if _is_safe_ref_token "$seg_target"; then
            branch="$seg_target"
          else
            branch="$_AMBIGUOUS_BRANCH_SENTINEL"
          fi
        elif [ -z "$double_dash" ] && [ -n "$first_pos" ]; then
          if _is_safe_ref_token "$first_pos"; then
            branch="$first_pos"
          else
            branch="$_AMBIGUOUS_BRANCH_SENTINEL"
          fi
        fi
      fi
      # Round 2 (2026-09-22, Bugbot): `git symbolic-ref HEAD <ref>` is a
      # THIRD way (alongside checkout/switch) of pointing HEAD at a
      # different branch — the tracker only recognized the first two, so
      # `git symbolic-ref HEAD refs/heads/main; git merge feature`
      # bypassed the deny entirely. `symbolic-ref` writes the ref
      # literally (no DWIM), so the operand is always a full ref path;
      # normalize it the same way as a full-ref-path checkout.
      if [[ "$seg" =~ ${_CMD_BOUNDARY}git[[:space:]]+symbolic-ref([[:space:]]|$) ]]; then
        symref_target=""
        prev="" seen=""
        for word in $seg; do
          if [ -z "$seen" ]; then
            if [ "$prev" = "git" ] && [ "$word" = "symbolic-ref" ]; then
              seen=1
            fi
            prev="$word"
            continue
          fi
          case "$word" in
            HEAD) : ;;
            -*) ;;
            *) [ -z "$symref_target" ] && symref_target="$word" ;;
          esac
        done
        # Round 5 (2026-09-23, Bugbot): only checkout/switch got the round-4
        # conservative-deny sentinel — symbolic-ref still just left the
        # PRIOR $branch value in place on an unresolvable target, so
        # `git symbolic-ref HEAD $(echo refs/heads/main)` off a non-main
        # HEAD silently kept the tracker on the old (non-main) branch
        # instead of treating the ambiguous target as dangerous, unlike the
        # equivalent checkout form. Apply the identical sentinel treatment.
        if [ -n "$symref_target" ]; then
          if _is_safe_ref_token "$symref_target"; then
            branch="$symref_target"
          else
            branch="$_AMBIGUOUS_BRANCH_SENTINEL"
          fi
        fi
      fi
      if [[ "$seg" =~ ${_CMD_BOUNDARY}git[[:space:]]+${_GIT_MERGE_GLOBAL_OPTS}merge([[:space:]]|$) ]]; then
        # Round 3 (2026-09-23, Bugbot): the old check only asked "does
        # --ff-only appear ANYWHERE in this segment?", so it treated
        # `--ff-only` as sticky even when a LATER flag in the same
        # invocation overrides it. Real git flag parsing is last-wins for
        # this trio, so `git merge --ff-only --no-ff feature` performs an
        # ordinary (non-fast-forward-only) merge — verified live — but the
        # old regex still saw --ff-only and skipped the deny. Word-scan the
        # segment and track only the LAST of --ff-only/--no-ff/--ff seen;
        # only skip the deny when that last flag is --ff-only.
        local ff_word ff_state=""
        for ff_word in $seg; do
          case "$ff_word" in
            --ff-only) ff_state="ff-only" ;;
            --no-ff|--ff) ff_state="not-ff-only" ;;
          esac
        done
        if [ "$ff_state" != "ff-only" ]; then
          # ⛔ Bugbot review (2026-09-22, PR #1241): `git checkout
          # refs/heads/main` tracks $branch as the literal string
          # "refs/heads/main", which the bare main|master case arm below
          # never matched — a full-ref-path checkout silently bypassed the
          # deny. Strip a leading refs/heads/ before comparing (the only
          # form this repo's own docs/scripts use for a local branch ref);
          # refs/remotes/* is a detached-HEAD checkout, not a same-named
          # local branch, and is out of this fix's scope.
          # Round 4 (2026-09-23, Bugbot): re-resolve HEAD for a -C/--git-dir
          # flag on THIS merge invocation, or a preceding `cd` in the same
          # chain, before falling back to the textually-tracked $branch.
          local merge_check_branch
          merge_check_branch="$(_resolve_merge_check_branch "$raw_seg" "$effective_cwd" "$effective_gitdir")"
          local branch_check
          if [ -n "$merge_check_branch" ]; then
            branch_check="${merge_check_branch#refs/heads/}"
          else
            branch_check="${branch#refs/heads/}"
          fi
          case "$branch_check" in
            main|master|"$_AMBIGUOUS_BRANCH_SENTINEL") return 0 ;;
          esac
        fi
      fi
    done <<EOF
$(printf '%s' "$c" | tr ';&|' '\n\n\n')
EOF
  fi
  return 1
}

# raw ref deletion — archive-branch.sh's own internal-only primitive; no other
# caller should touch it directly. Bugbot review (2026-09-22, PR #1241): the
# original deny_patterns regex required `-d`/`--delete` IMMEDIATELY after
# `update-ref`, so any other flag placed first (`git update-ref --no-deref -d
# refs/heads/tmp`) walked straight past it — the exact "immediately after"
# bug this file's own `git clean` helper (above) already fixed once for a
# different command. Word-scan the whole "git update-ref" segment instead:
# the flag is exact-word `-d` or `--delete` anywhere, order-independent,
# mirroring _is_dangerous_git_clean's force-flag-anywhere scan.
_is_dangerous_update_ref() {
  local c="$1" seg word
  [[ "$c" =~ ${_CMD_BOUNDARY}git[[:space:]]+update-ref([[:space:]]|$) ]] || return 1
  while IFS= read -r seg; do
    [[ "$seg" =~ ${_CMD_BOUNDARY}git[[:space:]]+update-ref([[:space:]]|$) ]] || continue
    for word in $seg; do
      case "$word" in
        -d|--delete) return 0 ;;
        # Round 3 (2026-09-23, Bugbot): git's `--stdin` mode reads ref
        # updates (including `delete <ref>` / `option no-deref` lines)
        # from stdin, so the actual delete never appears as a `-d`/
        # `--delete` FLAG on the command line at all — the flag-only
        # scan above can never see it. We cannot reliably inspect what
        # a piped/heredoc stdin stream will contain, so treat `--stdin`
        # itself as dangerous (deny outright, matching this file's
        # under-blocking-never posture on constructs we can't fully
        # scan).
        --stdin) return 0 ;;
      esac
    done
  done <<EOF
$(printf '%s' "$c" | tr ';&|' '\n\n\n')
EOF
  return 1
}

# --- Pattern array (matched against the normalized command) ----------------
# The settings.json deny-list catches the top-level form; this catches them
# when nested / wrapped / reordered.
deny_patterns=(
  # git history / branch destruction
  'git[[:space:]]+push[[:space:]]+[^;&|]*--force([[:space:]]|$)'        # --force (allows --force-with-lease)
  'git[[:space:]]+push[[:space:]]+([^;&|]*[[:space:]])?-[A-Za-z]*f[A-Za-z]*([[:space:]]|$)'  # -f in ANY bundled short-flag cluster (git push -uf), order-independent like _has_recursive; does NOT match --force-with-lease
  'git[[:space:]]+push[[:space:]][^;&|]*[[:space:]]\+[A-Za-z0-9_./@~^-]+'  # refspec force-push: git push origin +HEAD:main
  'git[[:space:]]+push[[:space:]]+[^;&|]*--mirror([[:space:]]|$)'       # --mirror force-updates every ref + deletes remote refs absent locally
  'git[[:space:]]+reset[[:space:]]+--hard([[:space:]]+|$)'
  # NB: git force-branch-delete (_is_dangerous_git_branch_delete), remote-branch
  # deletion (_is_dangerous_git_push_delete), and `git clean` force
  # (_is_dangerous_git_clean) are handled by the order-independent structural
  # helpers below, not a pattern — the old contiguous-anchor `git clean` pattern
  # missed the separated-token `git clean -d -f` form.
  # remote-code-exec via pipe / process- or command-substitution to an interpreter
  '(curl|wget)[^|]*\|[[:space:]]*(sudo[[:space:]]+)?(env[[:space:]]+[^[:space:]]+[[:space:]]+)?([^[:space:]|]*/)?([a-z]*sh|python[0-9.]*|perl|ruby|node)([[:space:]]|$)'
  # …and the multi-pipe / filter-then-execute evasion of the above: the single-pipe
  # form only inspects between curl/wget and the FIRST pipe, so `curl … | tee x | bash`
  # or `curl … | grep -v '#' | sh` slipped past. This catches an interpreter that is
  # the IMMEDIATE target of ANY pipe in a curl/wget chain (the interpreter right after
  # a `|`), so `… | grep python` is NOT matched (grep, not python, is the pipe target).
  '(curl|wget).*\|[[:space:]]*(sudo[[:space:]]+)?(env[[:space:]]+[^[:space:]]+[[:space:]]+)?([^[:space:]|]*/)?([a-z]*sh|python[0-9.]*|perl|ruby|node)([[:space:]]|$)'
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
  # destructive DELETE-verb API call. Bugbot review (2026-09-22, PR #1241): the
  # original pattern only matched the short `-X` flag, so `gh api ... --method
  # DELETE` and `curl ... --request DELETE` — the documented long-form spelling
  # of the exact same verb on both tools — sailed through. `--method` isn't a
  # real curl flag and `--request` isn't a real gh flag; harmlessly matching
  # both against both tools is a wider net, never a narrower one.
  # Round 2 (2026-09-22): the flag/value separator was `[[:space:]]*`, which
  # cannot match a literal `=` — so `--method=DELETE` / `--request=DELETE`
  # (the equals-attached long-flag form both tools accept) sailed through.
  # Widened to `[[:space:]=]*` and the trailing boundary to `${_CMD_END}` so
  # a chained/piped/newline-terminated command is still caught, matching the
  # boundary discipline used elsewhere in this file.
  # Round 4 (2026-09-23, Bugbot): the DELETE literal was case-sensitive, so
  # `--method delete` / `-X delete` / `--method=delete` (curl and gh both
  # accept a lowercase verb) sailed through untouched. Rather than `shopt -s
  # nocasematch` for the whole array (which would also loosen every OTHER
  # pattern matched in the same loop below — unintended side effects on
  # unrelated hard rules), spell DELETE as an explicit per-letter character
  # class so only this one pattern is case-insensitive.
  "(gh[[:space:]]+api|curl)[^;&|]*(-X|--method|--request)[[:space:]=]*[Dd][Ee][Ll][Ee][Tt][Ee]${_CMD_END}"
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
if _is_dangerous_git_push_delete "$norm";   then _deny "git-push-remote-branch-delete"; fi
if _is_dangerous_git_clean "$norm";         then _deny "git-clean-force"; fi
if _is_dangerous_merge "$norm" "$_norm_before_gitstrip";      then _deny "bypass-shaped-merge"; fi
if _is_dangerous_update_ref "$norm"; then _deny "git-update-ref-delete"; fi

# Then the pattern array.
for pat in "${deny_patterns[@]}"; do
  if [[ "$norm" =~ $pat ]]; then _deny "$pat"; fi
done

exit 0
