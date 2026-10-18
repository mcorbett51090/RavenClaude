#!/usr/bin/env python3
"""Gate 306 — headless ``claude -p`` call shape.

Every code site in this repo that runs ``claude -p`` must pass
``--strict-mcp-config`` or carry a reasoned exemption in
``tests/fixtures/headless-call-shape-exemptions.json``.

Why: ``--tools ""`` removes built-in tools but does not keep MCP tool
definitions out of the request prefix. Measured 2026-10-14
(docs/plans/2026-10-14-prompt-caching/analysis.md, E9): about 211,798 input
tokens with ``--tools ""`` alone, about 3,470 with ``--strict-mcp-config`` too.
Caching made the large prefix cheap to re-read, not free, and every cold call
paid for all of it.

It also rejects the variadic trap. ``--tools`` takes a list, so a positional
argument straight after ``--tools ""`` is read as a tool name and the prompt is
lost ("Input must be provided either through stdin or as a prompt argument").
``--tools=""`` is always safe.

Discovery (what counts as a site):
  * ``.sh`` files and extensionless files under a ``bin/`` dir: ``claude -p`` (or
    ``"$claude" -p`` / ``"${CLAUDE_BIN}" -p``) in command position (line start, after ``&&`` ``||`` ``;`` ``|`` ``(`` ``$(``,
    or after ``timeout N`` / ``_rc_timeout N``), on a non-comment line.
  * ``.js`` / ``.mjs``: the same command-position rule, skipping ``//`` lines.
  * ``.py``: the list form ``["claude", "-p", ...]`` only, where the first element
    is the literal ``"claude"``, a variable with ``claude`` in its name, or a
    resolver call such as ``_claude_bin()``. A shell-string
    ``"claude -p ..."`` in Python is not discovered (stated limit).
Known blind spots: a binary variable whose name lacks ``claude``, a call in a
language not listed, and a Python shell string. The positive control below
fails if discovery stops finding the known sites.

Exemptions are keyed by path with the number of sites in that file. A changed
site count, a missing reason, or a file that no longer needs the exemption is a
violation. That stops an exemption from silently covering an ADDED call, but not
a SWAPPED one: replacing one exempt call with a different unflagged call leaves
the count unchanged and passes. The flag check is a substring test, so the flag
inside a trailing comment also satisfies it. ``--print`` forms and ``.github/``
are not scanned. This is a lint, not a control.

Exit codes: 0 clean, 2 violation, 1 could not run.
Usage:
  check-headless-call-shape.py                       # check the real tree
  check-headless-call-shape.py --list                # print every discovered site
  check-headless-call-shape.py --self-test           # synthetic fixtures
  check-headless-call-shape.py --must-fail           # mutant: strip the flag from a
                                                     # real site; exits 3 if caught
  check-headless-call-shape.py --must-fail-convention  # prints the teeth exit
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

EXEMPTIONS_REL = "tests/fixtures/headless-call-shape-exemptions.json"
# This file holds call-site fixtures as test data (and quotes the shapes in its own
# docstring), so it is never scanned. Without this the gate flags itself once the
# file is tracked.
SELF_REL = "scripts/check-headless-call-shape.py"
SCAN_ROOTS = ("plugins/", "scripts/", ".claude/workflows/")
LEAN_FLAG = "--strict-mcp-config"
TEETH_EXIT = 3

# Positive control: discovery must keep finding at least these sites.
KNOWN_SITES = {
    "plugins/ravenclaude-core/scripts/thing-seat.sh": 2,
    "plugins/ravenclaude-core/scripts/claude-orchestrate.sh": 1,
    "plugins/ravenclaude-core/scripts/prompt-optimizer-gate.sh": 2,
    "plugins/ravenclaude-core/scripts/thing-decide.py": 2,
    "plugins/ravenclaude-core/scripts/prompt-optimizer-judge-soak.py": 1,
}

_CMD_POS = re.compile(
    r"(?:^|&&|\|\||[;|(]|\$\(|\b_?(?:rc_)?timeout\s+\S+\s+)\s*"
    r"(?:claude|\"?\$\{?\w*claude\w*\}?\"?)\s+-p\b",
    re.IGNORECASE,
)
# "claude", a variable holding the resolved binary (thing-decide.py: `claude`), or a
# resolver call such as _claude_bin().
_PY_LIST = re.compile(r"""\[\s*(?:["']claude["']|\w*claude\w*(?:\(\))?)\s*,\s*["']-p["']""")
_SHELL_END = {")", ">", "2>", "|", "||", "&&", ";", "&", ">/dev/null", "2>&1"}


class Site:
    def __init__(self, path: str, line: int, window: str, lang: str):
        self.path = path
        self.line = line
        self.window = window
        self.lang = lang

    def __repr__(self) -> str:
        return f"{self.path}:{self.line}"


def _lang(path: str) -> str | None:
    if path.endswith(".sh"):
        return "sh"
    if path.endswith(".py"):
        return "py"
    if path.endswith((".js", ".mjs")):
        return "js"
    parts = path.split("/")
    if len(parts) >= 2 and parts[-2] == "bin" and "." not in parts[-1]:
        return "sh"
    return None


def _shell_window(lines: list[str], i: int, cont: str) -> str:
    out = [lines[i]]
    j = i
    while out[-1].rstrip().endswith(cont) and j + 1 < len(lines):
        j += 1
        out.append(lines[j])
    return "\n".join(out)


def _py_window(text: str, start: int) -> str:
    depth = 0
    for k in range(start, len(text)):
        ch = text[k]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return text[start : k + 1]
    return text[start:]


def discover(path: str, text: str) -> list[Site]:
    lang = _lang(path)
    if lang is None or path == SELF_REL:
        return []
    sites: list[Site] = []
    if lang == "py":
        for m in _PY_LIST.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            sites.append(Site(path, line, _py_window(text, m.start()), "py"))
        return sites
    lines = text.split("\n")
    comment = "#" if lang == "sh" else "//"
    cont = "\\" if lang == "sh" else "+"
    for i, raw in enumerate(lines):
        stripped = raw.lstrip()
        if stripped.startswith(comment) or (lang == "js" and stripped.startswith("*")):
            continue
        if _CMD_POS.search(raw):
            sites.append(Site(path, i + 1, _shell_window(lines, i, cont), lang))
    return sites


def _variadic_trap(site: Site) -> bool:
    if site.lang == "py":
        toks = re.findall(r"""\*?\w+|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'""", site.window)
        for k, tok in enumerate(toks):
            if tok in ('"--tools"', "'--tools'") and k + 1 < len(toks):
                if toks[k + 1] in ('""', "''"):
                    nxt = toks[k + 2] if k + 2 < len(toks) else None
                    if nxt is not None and not re.match(r"""^["']-""", nxt):
                        return True
        return False
    # sh / js: --tools "" (or '') followed by a positional.
    flat = re.sub(r"\\\n", " ", site.window)
    flat = re.sub(r"[`'\"]\s*\+\s*\n\s*[`'\"]", " ", flat)
    for m in re.finditer(r"--tools\s+(?:\"\"|'')", flat):
        rest = flat[m.end() :].split()
        if not rest:
            continue
        nxt = rest[0]
        if nxt.startswith("-") or nxt in _SHELL_END or nxt.startswith((")", ">", "2>", "`")):
            continue
        return True
    return False


def check_sites(sites: list[Site], exemptions: dict) -> list[str]:
    problems: list[str] = []
    by_file: dict[str, list[Site]] = {}
    for s in sites:
        by_file.setdefault(s.path, []).append(s)
    for path, fsites in sorted(by_file.items()):
        for s in fsites:
            if _variadic_trap(s):
                problems.append(
                    f"{s}: `--tools \"\"` is followed by a positional argument; "
                    "--tools is variadic, so the prompt is lost. Use --tools=\"\" "
                    "or put a flag between them."
                )
        missing = [s for s in fsites if LEAN_FLAG not in s.window]
        ex = exemptions.get(path)
        if ex is None:
            for s in missing:
                problems.append(
                    f"{s}: claude -p without {LEAN_FLAG}. Add it (before --tools), "
                    f"or exempt the file in {EXEMPTIONS_REL} with a reason."
                )
            continue
        reason = str(ex.get("reason", "")).strip()
        if len(reason) < 20:
            problems.append(f"{path}: exemption needs a reason of at least 20 chars.")
        if ex.get("sites") != len(fsites):
            problems.append(
                f"{path}: exemption says {ex.get('sites')} site(s), found {len(fsites)}. "
                "Re-review the new call(s) and update the count."
            )
        if not missing:
            problems.append(
                f"{path}: every site already passes {LEAN_FLAG}; remove the stale exemption."
            )
    for path in sorted(set(exemptions) - set(by_file)):
        problems.append(f"{path}: exemption names a file with no claude -p site; remove it.")
    return problems


def _tracked_files(root: Path) -> list[str]:
    r = subprocess.run(
        ["git", "ls-files", "-z", "--", *SCAN_ROOTS],
        cwd=root,
        capture_output=True,
        check=True,
    )
    out = []
    for p in r.stdout.decode("utf-8", "replace").split("\0"):
        if p and "/tests/fixtures/" not in f"/{p}" and _lang(p) is not None:
            out.append(p)
    return out


def scan_tree(root: Path, files: list[str] | None = None) -> list[Site]:
    files = files if files is not None else _tracked_files(root)
    sites: list[Site] = []
    for rel in files:
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        sites.extend(discover(rel, text))
    return sites


def load_exemptions(root: Path) -> dict:
    p = root / EXEMPTIONS_REL
    data = json.loads(p.read_text(encoding="utf-8"))
    return data.get("exemptions", {})


def positive_control(sites: list[Site]) -> list[str]:
    counts: dict[str, int] = {}
    for s in sites:
        counts[s.path] = counts.get(s.path, 0) + 1
    bad = []
    for path, n in KNOWN_SITES.items():
        if counts.get(path, 0) < n:
            bad.append(
                f"positive control: expected >= {n} site(s) in {path}, found "
                f"{counts.get(path, 0)}. Discovery is broken, so a clean result means nothing."
            )
    return bad


def run_real(root: Path) -> int:
    try:
        sites = scan_tree(root)
        exemptions = load_exemptions(root)
    except (OSError, ValueError, subprocess.CalledProcessError) as e:
        print(f"check-headless-call-shape: could not run: {e}", file=sys.stderr)
        return 1
    problems = positive_control(sites) + check_sites(sites, exemptions)
    if problems:
        print("headless call shape: FAIL", file=sys.stderr)
        for p in problems:
            print(f"  ✗ {p}", file=sys.stderr)
        return 2
    print(
        f"headless call shape: OK — {len(sites)} site(s), "
        f"{len(exemptions)} exempt file(s), positive control held."
    )
    return 0


# ── self-test ────────────────────────────────────────────────────────────────
_FIX = {
    "ok.sh": 'raw="$(cd "$d" && claude -p \\\n  --strict-mcp-config \\\n  --tools "" \\\n  --append-system-prompt "$S" \\\n  "$p")"\n',
    "missing.sh": 'raw="$(claude -p --output-format json --tools "" \\\n  --append-system-prompt "$S" "$p")"\n',
    "trap.sh": 'raw="$(claude -p --strict-mcp-config --tools "" "$p")"\n',
    "eq.sh": 'raw="$(_rc_timeout 3 claude -p --strict-mcp-config --tools="" "$p")"\n',
    "usage/bin/rc": "cat <<EOF\n  rc cache-report   Sum headless claude -p usage\nEOF\n",
    "comment.sh": "# we call claude -p --tools '' here\necho hi\n",
    "ok.py": 'subprocess.run(["claude", "-p", "--strict-mcp-config", "--tools", "", "--model", m, prompt])\n',
    "missing.py": 'subprocess.run(\n    [\n        "claude",\n        "-p",\n        "--model",\n        m,\n        prompt,\n    ]\n)\n',
    "trap.py": 'subprocess.run(["claude", "-p", "--strict-mcp-config", "--tools", "", prompt])\n',
    "doc.py": '"""Shell out to `claude -p` for the judge."""\n',
    "ok.js": "const s =\n  `timeout 2 claude -p --strict-mcp-config --bare ` +\n  `--model x 'prompt'`;\n",
    "exempt.sh": 'claude -p --bare --tools="" "$p"\n',
    "var.py": 'claude = _claude_bin()\nsubprocess.run([claude, "-p", "--model", m, prompt])\n',
    "var.sh": 'out="$("$claude_bin" -p --output-format json "$p")"\n',
}


def _self_test() -> int:
    ran: list[tuple[str, bool]] = []

    def check(name: str, cond: bool) -> None:
        ran.append((name, cond))
        print(f"  {'✓' if cond else '✗'} {name}")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for rel, body in _FIX.items():
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body)
        files = list(_FIX)
        sites = scan_tree(root, files)
        found = {s.path for s in sites}
        check("discovers shell site", "ok.sh" in found and "missing.sh" in found)
        check("discovers --tools= shell site", "eq.sh" in found)
        check("discovers python list site across lines", "missing.py" in found)
        check("discovers js template site", "ok.js" in found)
        check("ignores heredoc usage text", "usage/bin/rc" not in found)
        check("ignores comment line", "comment.sh" not in found)
        check("ignores python docstring mention", "doc.py" not in found)
        check("discovers python resolved-binary variable", "var.py" in found)
        check("discovers shell binary variable", "var.sh" in found)
        check(
            "never scans its own fixture text",
            discover(SELF_REL, _FIX["trap.py"] + _FIX["missing.sh"]) == [],
        )

        def probs(only: str, ex: dict | None = None) -> list[str]:
            return check_sites([s for s in sites if s.path == only], ex or {})

        check("compliant shell passes", probs("ok.sh") == [])
        check("compliant python passes", probs("ok.py") == [])
        check("compliant js passes", probs("ok.js") == [])
        check("--tools=\"\" form is not a trap", probs("eq.sh") == [])
        check("shell missing flag fails", any(LEAN_FLAG in p for p in probs("missing.sh")))
        check("python missing flag fails", any(LEAN_FLAG in p for p in probs("missing.py")))
        check("shell variadic trap fails", any("variadic" in p for p in probs("trap.sh")))
        check("python variadic trap fails", any("variadic" in p for p in probs("trap.py")))
        good = {"exempt.sh": {"sites": 1, "reason": "already --bare; pairing with strict-mcp unmeasured"}}
        check("reasoned exemption passes", probs("exempt.sh", good) == [])
        bad_count = {"exempt.sh": {"sites": 2, "reason": good["exempt.sh"]["reason"]}}
        check("wrong site count fails", any("site(s)" in p for p in probs("exempt.sh", bad_count)))
        short = {"exempt.sh": {"sites": 1, "reason": "x"}}
        check("short reason fails", any("reason" in p for p in probs("exempt.sh", short)))
        stale = {"ok.sh": {"sites": 1, "reason": "this file used to need an exemption"}}
        check("stale exemption on a compliant file fails", any("stale" in p for p in probs("ok.sh", stale)))
        orphan = check_sites([], {"gone.sh": {"sites": 1, "reason": "file was deleted long ago"}})
        check("exemption for a file with no site fails", any("no claude -p site" in p for p in orphan))
        ctrl = positive_control([])
        check("positive control fails on empty discovery", len(ctrl) == len(KNOWN_SITES))

    failed = [n for n, ok in ran if not ok]
    print(f"check-headless-call-shape --self-test: {len(ran) - len(failed)}/{len(ran)} passed")
    return 0 if not failed else 2


def _must_fail(root: Path) -> int:
    """Copy one real compliant site, strip the flag, and require a violation."""
    rel = "plugins/ravenclaude-core/scripts/thing-seat.sh"
    src = root / rel
    try:
        text = src.read_text(encoding="utf-8")
    except OSError as e:
        print(f"must-fail: could not read {rel}: {e}", file=sys.stderr)
        return 1
    mutant = "\n".join(ln for ln in text.split("\n") if LEAN_FLAG not in ln)
    if mutant == text:
        print(f"must-fail: {rel} carries no {LEAN_FLAG}; mutant is a no-op", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / Path(rel).parent
        d.mkdir(parents=True)
        (d / Path(rel).name).write_text(mutant)
        sites = scan_tree(Path(td), [rel])
        caught = any(LEAN_FLAG in p for p in check_sites(sites, {}))
    print(f"must-fail: stripped {LEAN_FLAG} from {rel} -> {'caught' if caught else 'NOT caught'}")
    return TEETH_EXIT if caught else 0


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parent.parent
    if "--must-fail-convention" in argv:
        print(f"must-fail-teeth-exit: {TEETH_EXIT}")
        return 0
    if "--self-test" in argv:
        return _self_test()
    if "--must-fail" in argv:
        return _must_fail(root)
    if "--list" in argv:
        for s in scan_tree(root):
            flag = "lean" if LEAN_FLAG in s.window else "no-flag"
            print(f"{s}\t{flag}")
        return 0
    return run_real(root)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
