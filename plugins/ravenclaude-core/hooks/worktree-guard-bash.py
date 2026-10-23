#!/usr/bin/env python3
"""Best-effort Bash write-target check for worktree-guard.
argv: <worktree_root> <cwd>; stdin: the bash command string.
exit 0 = no out-of-tree write found; 3 = out-of-tree write (reason on stdout).
Any other exit / exception => caller fails CLOSED.
Shell parsing here is BEST-EFFORT (no eval, vars/globs/subshell tricks can
evade it). The real backstop is the bwrap sandbox write allowlist."""
import os, re, shlex, sys

root, cwd = os.path.realpath(sys.argv[1]), sys.argv[2]
cmd = sys.stdin.read()
ALLOW = [root, "/tmp", "/var/tmp", "/dev/null", "/dev/stdout", "/dev/stderr", "/dev/fd", "/proc/self/fd"]
for _e in [os.environ.get("TMPDIR"), os.environ.get("RC_WG_GUARD_HOME"), "/workspace/cli-out"] + os.environ.get("RC_WG_EXTRA_WRITE_ROOTS", "").split(":"):
    if _e: ALLOW.append(os.path.realpath(_e))
bad = []

def outside(p):
    p = p.strip().strip("'\"")
    if not p or p.startswith("&") or p == "-": return False
    if p.startswith("$") or "$(" in p or "`" in p:
        return not p.startswith(("$TMPDIR", "${TMPDIR")) and not re.match(r"^\$\{?(PWD|CLAUDE_PROJECT_DIR)\}?(/|$)", p)
    p = os.path.expanduser(p)
    a = os.path.realpath(os.path.join(cwd, p))
    return not any(a == r or a.startswith(r.rstrip("/") + "/") for r in ALLOW)

def flag(kind, p):
    if outside(p): bad.append(f"{kind} -> {p}")

# 1. redirections > >> &> >| (skip fd dups like 2>&1)
for m in re.finditer(r"(?:^|[^<>&0-9])(?:[0-9]?|&)>>?\|?\s*([^\s;&|<>()]+)", cmd):
    flag("redirect", m.group(1))
# 2. heredoc bodies are data; analyse their command line only (already above).
segs = re.split(r"\|\||&&|;|\||\n", re.sub(r"<<-?\s*['\"]?(\w+)['\"]?.*?\n.*?\n\1\b", "<<HEREDOC", cmd, flags=re.S))
WRITERS = {"cp": "last", "mv": "last", "install": "last", "ln": "last", "rsync": "last",
           "rm": "all", "rmdir": "all", "mkdir": "all", "touch": "all", "truncate": "all",
           "chmod": "allbut1", "chown": "allbut1", "tee": "all", "dd": "of"}
for s in segs:
    try: toks = shlex.split(s, comments=False)
    except ValueError: toks = s.split()
    while toks and (re.match(r"^\w+=", toks[0]) or toks[0] in ("sudo", "env", "nohup", "time", "command", "exec", "xargs")):
        toks = toks[1:]
    if not toks: continue
    c = os.path.basename(toks[0]); args = [t for t in toks[1:] if not t.startswith("-")]
    if c == "sed" and any(t.startswith("-i") or t == "--in-place" for t in toks):
        for t in args[1:]: flag("sed -i", t)
    elif c in WRITERS:
        mode = WRITERS[c]
        if mode == "of": [flag(c, t[3:]) for t in toks if t.startswith("of=")]
        elif mode == "last" and args: flag(c, args[-1])
        elif mode == "allbut1": [flag(c, t) for t in args[1:]]
        elif mode == "all": [flag(c, t) for t in args]
    elif re.match(r"^(python[0-9.]*|node|nodejs|perl|ruby|php|deno|bun)$", c):
        code = " ".join(toks[1:])
        # inline (-c/-e) or heredoc/stdin programs: look for absolute/home path literals used in writes
        if any(t in ("-c", "-e", "-E", "--eval", "-") for t in toks) or "<<" in s or "<<HEREDOC" in s:
            pass
for m in re.finditer(r"(?:python[0-9.]*|node|perl|ruby)\b[^\n]*?(?:\s-[ceE]\s|\s-\s|<<)", cmd):
    # best-effort: any quoted absolute/~ path literal in the whole command that looks write-ish
    if re.search(r"open\([^)]*['\"][wax]b?\+?['\"]|write_text|write_bytes|writeFile|appendFile|createWriteStream|shutil\.|os\.(rename|replace|remove|unlink|makedirs|mkdir)|rmtree|unlinkSync|rmSync|open\s*\(?\s*\w+\s*,\s*['\"]\+?>|print\s*\{", cmd):
        for p in re.findall(r"['\"]((?:/|~/)[^'\"\s]*)['\"]", cmd):
            if not p.startswith(("/usr/", "/bin/", "/lib", "/etc/", "/opt/", "/proc/", "/sys/")): flag("inline-interpreter", p)
    break
if bad:
    print("; ".join(dict.fromkeys(bad))[:600]); sys.exit(3)
sys.exit(0)
