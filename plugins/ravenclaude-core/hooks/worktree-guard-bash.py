#!/usr/bin/env python3
"""Best-effort Bash write-target check for worktree-guard.
argv: <worktree_root> <cwd>; stdin: the bash command string.
exit 0 = no out-of-tree write found; 3 = out-of-tree write (reason on stdout)
        or input exceeds the parse cap (reason "too large to parse").
exit 4 = self-timeout (SIGALRM) or the timer could not be armed.
Any other exit / exception => caller fails CLOSED.
Shell parsing here is BEST-EFFORT (no eval, vars/globs/subshell tricks can
evade it). The real backstop is the bwrap sandbox write allowlist.

AppSec N1 (SHIPCHECK on RavenClaude#1423, present since #1416): the prior
heredoc regex ``<<-?\\s*['\"]?(\\w+)['\"]?.*?\\n\\1\\b`` (re.S) was roughly
cubic on unterminated markers and could stall past Claude Code's 600 s
PreToolUse default, after which a timed-out hook does not block (fail open
on this box's Claude Code < 2.1.295). Defense in depth, all fail-closed:
(a) a hard input cap (64 KiB or more than 256 ``<<`` markers) exits 3;
(b) a line-based linear heredoc scanner replaces the regex;
(c) signal.alarm(5) exits 4 (worktree-guard.sh already maps unexpected
helper exits to a deny via _wg_fail_closed). SIGALRM is required: this
helper is invoked by a bash hook and is Unix-only; if the timer cannot
be armed, exit 4 (never fail open)."""
import os
import re
import shlex
import signal
import sys

# Documented, tested thresholds (AppSec N1). Fail closed on exceed, never open.
_MAX_CMD_CHARS = 64 * 1024  # 64 KiB of decoded stdin
_MAX_HEREDOC_MARKERS = 256
_ALARM_SECS = 5


def _on_alarm(signum, frame):
    # Immediate: do not run finally/flush paths that could exit 0.
    os._exit(4)


def _arm_alarm():
    if not hasattr(signal, "SIGALRM") or not hasattr(signal, "alarm"):
        sys.exit(4)
    try:
        signal.signal(signal.SIGALRM, _on_alarm)
        signal.alarm(_ALARM_SECS)
    except (AttributeError, ValueError, OSError):
        sys.exit(4)


def _disarm_alarm():
    try:
        if hasattr(signal, "alarm"):
            signal.alarm(0)
    except (AttributeError, ValueError, OSError):
        pass


def _read_cmd_capped():
    # One past the cap so a huge payload is denied without being fully slurped.
    data = sys.stdin.read(_MAX_CMD_CHARS + 1)
    if len(data) > _MAX_CMD_CHARS:
        print("too large to parse")
        sys.exit(3)
    return data


def _parse_heredoc_opener(text, idx):
    """If text[idx:] is a heredoc opener (not a here-string), return
    (tag, strip_tabs, end_index); otherwise None.

    The delimiter is the full bash word, not a leading \\w+ run (AppSec R1
    on RavenClaude#1424). Unquoted whitespace or a metacharacter ends the
    word. Quotes and backslashes are stripped and adjacent segments are
    concatenated: <<'EOF'X -> EOFX, <<"A"B -> AB, <<'E O F' -> 'E O F'
    (spaces preserved, quotes removed so the terminator line is "E O F"),
    <<\\PY -> PY, <<EOF-X / <<E.O.F / <<END-MSG keep the punctuation.
    <<< is a here-string and is not a heredoc. <<- strips leading tabs
    on the terminator line.
    """
    if not text.startswith("<<", idx):
        return None
    if idx + 2 < len(text) and text[idx + 2] == "<":
        return None  # here-string <<<
    j = idx + 2
    strip_tabs = False
    if j < len(text) and text[j] == "-":
        strip_tabs = True
        j += 1
    while j < len(text) and text[j] in " \t":
        j += 1
    word, j = _parse_shell_word(text, j)
    if not word:
        return None
    return word, strip_tabs, j


# Unquoted, these end a bash word (IFS whitespace + metacharacters).
_WORD_END = frozenset(" \t\n|&;()<>")


def _parse_shell_word(text, j):
    """Read one bash word starting at j. Returns (dequoted_word, end_index).

    Empty word means there was no word. End index is the first unquoted
    word-ending character (or len(text)); it is not consumed.
    """
    n = len(text)
    if j >= n or text[j] in _WORD_END:
        return "", j
    parts = []
    while j < n and text[j] not in _WORD_END:
        c = text[j]
        if c == "'":
            j += 1
            start = j
            while j < n and text[j] != "'":
                j += 1
            parts.append(text[start:j])
            if j < n and text[j] == "'":
                j += 1
            continue
        if c == '"':
            j += 1
            buf = []
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n and text[j + 1] in "$`\"\\\n":
                    buf.append(text[j + 1])
                    j += 2
                    continue
                buf.append(text[j])
                j += 1
            parts.append("".join(buf))
            if j < n and text[j] == '"':
                j += 1
            continue
        if c == "\\":
            j += 1
            if j >= n:
                break
            if text[j] == "\n":
                j += 1  # line continuation, not part of the delimiter
                continue
            parts.append(text[j])
            j += 1
            continue
        start = j
        while j < n and text[j] not in _WORD_END and text[j] not in "'\"\\":
            j += 1
        parts.append(text[start:j])
    return "".join(parts), j


def _is_terminator(line, tag, strip_tabs):
    # Bash requires the delimiter alone on the line (leading tabs stripped
    # only for <<-). Exact match — not a leading-\\w+ / word-boundary guess.
    if line.endswith("\r"):
        line = line[:-1]
    check = line.lstrip("\t") if strip_tabs else line
    return check == tag


_INTERP_NAME_RE = re.compile(r"^(?:python[0-9.]*|node|nodejs|perl|ruby|php|deno|bun)$")


def _heredoc_feeds_interpreter(prefix):
    # The simple command immediately before `<<` (e.g. `python3 - <<'PY'`).
    seg = re.split(r"[\n;&|(]", prefix)[-1]
    for tok in seg.split():
        tok = tok.strip("'\"").lstrip("\\")
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", tok):
            continue  # a leading VAR=val assignment is not the command word
        if _INTERP_NAME_RE.match(os.path.basename(tok)):
            return True
    return False


def _strip_data_heredocs(text, keep_interpreter, blank):
    """Line-based linear replacement for the old ``.*?\\n\\1\\b`` regex.

    Walks the string once. Terminated data heredocs are replaced with
    `blank`. Interpreter-fed heredocs are kept whole when keep_interpreter
    is True so the body (the program) is scanned. If a terminator is not
    found, or the opener cannot be parsed, the rest of the command is
    kept in the output (AppSec R1): never drop unscanned text. Linear —
    a missing terminator does not backtrack.
    """
    n = len(text)
    out = []
    pos = 0
    while pos < n:
        idx = text.find("<<", pos)
        if idx < 0:
            out.append(text[pos:])
            break
        parsed = _parse_heredoc_opener(text, idx)
        if parsed is None:
            out.append(text[pos : idx + 2])
            pos = idx + 2
            continue
        tag, strip_tabs, opener_end = parsed
        keep = keep_interpreter and _heredoc_feeds_interpreter(text[:idx])
        nl = text.find("\n", opener_end)
        if keep:
            if nl < 0:
                out.append(text[pos:])
                break
            k = nl + 1
            found = False
            while k <= n:
                line_end = text.find("\n", k)
                if line_end < 0:
                    line = text[k:]
                    next_k = n
                else:
                    line = text[k:line_end]
                    next_k = line_end + 1
                if _is_terminator(line, tag, strip_tabs):
                    out.append(text[pos:next_k])
                    pos = next_k
                    found = True
                    break
                if line_end < 0:
                    break
                k = next_k
            if not found:
                out.append(text[pos:])
                break
        else:
            if nl < 0:
                # Unterminated (no body line): keep the rest, including any
                # later commands on this or following lines.
                out.append(text[pos:])
                break
            k = nl + 1
            found = False
            while k <= n:
                line_end = text.find("\n", k)
                if line_end < 0:
                    line = text[k:]
                    next_k = n
                else:
                    line = text[k:line_end]
                    next_k = line_end + 1
                if _is_terminator(line, tag, strip_tabs):
                    out.append(text[pos:idx] + blank)
                    pos = next_k
                    found = True
                    break
                if line_end < 0:
                    break
                k = next_k
            if not found:
                # Unterminated: keep opener, body, and everything after.
                out.append(text[pos:])
                break
    return "".join(out)


def main():
    _arm_alarm()
    try:
        root, cwd = os.path.realpath(sys.argv[1]), os.path.realpath(sys.argv[2])
        cmd = _read_cmd_capped()
        if cmd.count("<<") > _MAX_HEREDOC_MARKERS:
            print("too large to parse")
            sys.exit(3)

        ALLOW = [root, "/tmp", "/var/tmp", "/dev/null", "/dev/stdout", "/dev/stderr", "/dev/fd", "/proc/self/fd"]
        # Copilot Chat with no project uses ~/.copilot/chats/<id> as cwd. Writes inside
        # that one session folder are the chat's own scratch, not a sibling worktree.
        _chats = os.path.realpath(os.path.expanduser("~/.copilot/chats"))
        if cwd == _chats or cwd.startswith(_chats + os.sep):
            ALLOW.append(cwd)
        for _e in [os.environ.get("TMPDIR"), os.environ.get("RC_WG_GUARD_HOME"), "/workspace/cli-out"] + os.environ.get("RC_WG_EXTRA_WRITE_ROOTS", "").split(":"):
            if _e:
                ALLOW.append(os.path.realpath(_e))
        bad = []

        def outside(p):
            p = p.strip().strip("'\"")
            if not p or p.startswith("&") or p == "-":
                return False
            if "$(" in p or "`" in p:
                return True
            if "$" in p:
                expanded = os.path.expandvars(p)
                if expanded == p or "$" in expanded:
                    return not p.startswith(("$TMPDIR", "${TMPDIR")) and not re.match(r"^\$\{?(PWD|CLAUDE_PROJECT_DIR)\}?(/|$)", p)
                p = expanded
            p = os.path.expanduser(p)
            a = os.path.realpath(os.path.join(cwd, p))
            return not any(a == r or a.startswith(r.rstrip("/") + "/") for r in ALLOW)

        def flag(kind, p):
            if outside(p):
                bad.append(f"{kind} -> {p}")

        # 1. redirections > >> &> >| (skip fd dups like 2>&1)
        for m in re.finditer(r"(?:^|[^<>&0-9])(?:[0-9]?|&)>>?\|?\s*([^\s;&|<>()]+)", cmd):
            flag("redirect", m.group(1))
        # 2. heredoc bodies are data; analyse their command line only (already above).
        # Linear scanner (AppSec N1) — same blanking as the old regex, no backtracking.
        segs = re.split(r"\|\||&&|;|\||\n", _strip_data_heredocs(cmd, keep_interpreter=False, blank="<<HEREDOC\n"))
        WRITERS = {"cp": "last", "mv": "last", "install": "last", "ln": "last", "rsync": "last",
                   "rm": "all", "rmdir": "all", "mkdir": "all", "touch": "all", "truncate": "all",
                   "chmod": "allbut1", "chown": "allbut1", "tee": "all", "dd": "of"}
        for s in segs:
            try:
                toks = shlex.split(s, comments=False)
            except ValueError:
                toks = s.split()
            while toks and (re.match(r"^\w+=", toks[0]) or toks[0] in ("sudo", "env", "nohup", "time", "command", "exec", "xargs")):
                toks = toks[1:]
            if not toks:
                continue
            c = os.path.basename(toks[0]); args = [t for t in toks[1:] if not t.startswith("-")]
            if c == "sed" and any(t.startswith("-i") or t == "--in-place" for t in toks):
                for t in args[1:]:
                    flag("sed -i", t)
            elif c in WRITERS:
                mode = WRITERS[c]
                if mode == "of":
                    [flag(c, t[3:]) for t in toks if t.startswith("of=")]
                elif mode == "last" and args:
                    flag(c, args[-1])
                elif mode == "allbut1":
                    [flag(c, t) for t in args[1:]]
                elif mode == "all":
                    [flag(c, t) for t in args]
            elif re.match(r"^(python[0-9.]*|node|nodejs|perl|ruby|php|deno|bun)$", c):
                # inline (-c/-e) or heredoc/stdin programs: look for absolute/home path literals used in writes
                if any(t in ("-c", "-e", "-E", "--eval", "-") for t in toks) or "<<" in s or "<<HEREDOC" in s:
                    pass
        # Heredoc bodies are data UNLESS the heredoc feeds an interpreter — then the
        # body IS the program that runs, and blanking it (as the straight-command
        # WRITERS loop above correctly does for a plain data heredoc) would let the
        # body's own writes slip past every pattern below. #1416 (cba447ec) started
        # stripping every heredoc body unconditionally before this scan ever ran;
        # AppSec SHIPCHECK 18f5c03f (F1) reproduced the resulting bypass:
        # `python3 - <<'PY'` / `open(...,'w')`, `python3 <<PY` / `shutil.rmtree(...)`,
        # `node <<JS` / `fs.writeFileSync(...)` all returned exit 0 (allow). Scoped to
        # the DIRECT form (`<interpreter> [flags] <<TAG`) to match the WRITERS-loop
        # command-word check two blocks above, which is the same shape — a heredoc
        # piped INTO an interpreter (`cat <<EOF | python3`) is not detected here
        # either, same best-effort limit this file's own docstring already states. A
        # plain data heredoc (`cat <<EOF`, `git commit -F - <<EOF`) is still blanked,
        # so an example path inside its body does not false-deny. Interpreter set
        # matches the WRITERS-loop check: python/python3, node, nodejs, perl, ruby,
        # php, deno, bun.
        # AppSec N1: the interpreter-vs-data decision is still made per opener
        # (via _heredoc_feeds_interpreter) but the walk is line-based and linear.
        _scan = _strip_data_heredocs(cmd, keep_interpreter=True, blank=" <<HEREDOC\n")
        for _m in re.finditer(r"(?:python[0-9.]*|node|nodejs|perl|ruby|php|deno|bun)\b[^\n]*?(?:\s-[ceE]\s|\s-\s|<<)", _scan):
            # best-effort: any quoted absolute/~ path literal in the whole command that looks write-ish
            if re.search(r"open\([^)]*['\"][wax]b?\+?['\"]|write_text|write_bytes|writeFile|writeTextFile|file_put_contents|appendFile|createWriteStream|shutil\.|os\.(rename|replace|remove|unlink|makedirs|mkdir)|rmtree|unlinkSync|rmSync|Bun\.write|open\s*\(?\s*\w+\s*,\s*['\"]\+?>|print\s*\{", _scan):
                for p in re.findall(r"['\"]((?:/|~/)[^'\"\s]*)['\"]", _scan):
                    if not p.startswith(("/usr/", "/bin/", "/lib", "/etc/", "/opt/", "/proc/", "/sys/")):
                        flag("inline-interpreter", p)
            break
        if bad:
            print("; ".join(dict.fromkeys(bad))[:600])
            sys.exit(3)
        sys.exit(0)
    finally:
        _disarm_alarm()


if __name__ == "__main__":
    main()
