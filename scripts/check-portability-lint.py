#!/usr/bin/env python3
"""CI backstop for the macOS-portability banned-token set.

The `macos-latest` runner is the behavioural gate — it EXECUTES the hooks under
a stock toolchain and is the only thing that can catch a runtime-only break.
This is the static, author-time complement: it reads the same token table the
in-loop hook reads and scans the whole scoped tree, so a break is named on the
PR that introduces it rather than on whichever later PR happens to run the
affected code path.

Both surfaces read `plugins/ravenclaude-core/knowledge/portability-tokens.json`.
Neither hard-codes a pattern, so they cannot disagree — the parity is structural.
Anything else would be two hand-maintained lists, which is the drift this
initiative exists to prevent.

Scope reaches past hooks/ deliberately: the two most recent real breaks were in
an extension-less installer and a monitors script, both outside `hooks/**`.

Exit codes:  0 = clean;  2 = a finding, or the table could not be read.
Exit 1 is never used for a finding.

Usage:
    python3 scripts/check-portability-lint.py
    python3 scripts/check-portability-lint.py --report-only   # exit 0 always
    python3 scripts/check-portability-lint.py --self-test
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

TABLE = Path("plugins/ravenclaude-core/knowledge/portability-tokens.json")

# Files scanned. Extension-less entrypoints are named explicitly because a
# `*.sh` glob silently misses them — one of them is where break #885 landed.
SCOPE_GLOBS = [
    "plugins/*/hooks/*.sh",
    "plugins/*/monitors/*.sh",
    "scripts/*.sh",
]
SCOPE_FILES = ["scripts/ravenclaude"]
SCOPE_DIR_ANY = ["plugins/*/bin"]

# Sanctioned exemptions. Each of these must CONTAIN the banned tokens to do its
# job, so linting them would be the self-non-recursion failure: a guard that
# denies its own fix and its own test.
EXEMPT_NAMES = {
    "_portable.sh",             # the shims themselves
    "check-macos-portability.sh",  # the runtime runner; drives the real thing
    "check-portability-lint.py",   # this file
}
EXEMPT_PATH_PARTS = ("/tests/", "/fixtures/", "/test/")
SENTINEL = re.compile(r"#\s*noport\b")


class Finding(NamedTuple):
    path: str
    line: int
    token: str
    why: str
    shim: str

    def render(self) -> str:
        return (
            f"  {self.path}:{self.line}  [{self.token}]\n"
            f"      {self.why}\n"
            f"      use instead: {self.shim}"
        )


def load_tokens(table: Path = TABLE):
    try:
        data = json.loads(table.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"portability-lint: cannot read {table}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"portability-lint: {table} is not valid JSON: {exc}") from exc
    toks = data.get("tokens") or []
    if not toks:
        raise SystemExit(f"portability-lint: {table} declares no tokens — refusing to pass vacuously")
    out = []
    for t in toks:
        try:
            pair = t.get("portable_pair")
            out.append((
                t["id"],
                re.compile(t["pattern"]),
                t.get("why", ""),
                t.get("shim", ""),
                t.get("mode", "command"),
                re.compile(pair) if pair else None,
            ))
        except re.error as exc:
            raise SystemExit(f"portability-lint: token {t.get('id')!r} has an uncompilable pattern: {exc}")
        except KeyError as exc:
            raise SystemExit(f"portability-lint: token entry missing {exc}")
    return out


def is_exempt(p: Path) -> bool:
    if p.name in EXEMPT_NAMES:
        return True
    s = "/" + p.as_posix()
    return any(part in s for part in EXEMPT_PATH_PARTS)


def scoped_files(root: Path) -> list[Path]:
    seen = {}
    for g in SCOPE_GLOBS:
        for p in root.glob(g):
            if p.is_file():
                seen[p.resolve()] = p
    for f in SCOPE_FILES:
        p = root / f
        if p.is_file():
            seen[p.resolve()] = p
    for g in SCOPE_DIR_ANY:
        for d in root.glob(g):
            if d.is_dir():
                for p in d.iterdir():
                    if p.is_file():
                        seen[p.resolve()] = p
    return sorted(seen.values(), key=lambda x: x.as_posix())


_SQ = re.compile(r"'[^'\n]*'")
_DQ = re.compile(r"\"[^\"\n]*\"")


def _blank(m) -> str:
    return " " * len(m.group(0))


def _strip_comment(line: str) -> str:
    h = line.find("#")
    return line if h == -1 else line[:h] + " " * (len(line) - h)


def _preprocess(line: str, mode: str) -> str:
    """Reduce a line to the part where the token would actually be INVOKED.

    The question is behavioural — "is this run here?" — not "does this string
    appear?". Measured against the live tree, the naive string answer produced
    16 findings and every one was wrong: warning comments that name the banned
    token, quoted fixture strings inside a test corpus, case-glob matcher data,
    and deliberate GNU-then-BSD fallback pairs. A linter with that hit rate gets
    switched off in a day, which is worse than not having one.

    Quotes are blanked BEFORE comments so a '#' inside a string is not read as a
    comment start. Length is preserved so nothing shifts.

    Two modes, because they are not the same question:
      command   — a program invocation. Anything inside single OR double quotes
                  is an argument or data, not a command being run here.
      expansion — a shell parameter expansion. "${v^^}" inside double quotes is
                  a REAL use, so only single quotes (where no expansion happens
                  at all) are blanked. Treating these alike would trade a flood
                  of false positives for a silent false negative on the most
                  common form of the construct.
    """
    out = _SQ.sub(_blank, line)
    if mode == "command":
        out = _DQ.sub(_blank, out)
    return _strip_comment(out)


def scan_text(text: str, tokens, path: str = "<stdin>") -> list[Finding]:
    """Scan content line by line. A `# noport` line is skipped whole, and a token
    whose `portable_pair` appears nearby is a deliberate cross-platform idiom."""
    findings = []
    lines = text.splitlines()
    for i, raw in enumerate(lines, start=1):
        if SENTINEL.search(raw):
            continue
        for tok_id, rx, why, shim, mode, pair in tokens:
            if not rx.search(_preprocess(raw, mode)):
                continue
            # A GNU form with its BSD counterpart beside it is portable BY
            # CONSTRUCTION. The window is small and deliberate: these idioms put
            # the fallback on the same line or the very next one.
            if pair is not None:
                lo, hi = max(0, i - 3), min(len(lines), i + 2)
                if pair.search("\n".join(lines[lo:hi])):
                    continue
            findings.append(Finding(path, i, tok_id, why, shim))
    return sorted(findings, key=lambda f: (f.line, f.token))


def scan_repo(root: Path, tokens) -> list[Finding]:
    findings = []
    for p in scoped_files(root):
        if is_exempt(p):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        findings.extend(scan_text(text, tokens, p.as_posix()))
    return findings


# ── Teeth ────────────────────────────────────────────────────────────────────


def self_test() -> int:
    tokens = load_tokens()
    ok = True

    # Every declared token must be caught by a fixture built from its own id.
    # Assembled rather than written literally: this file is itself in scope for a
    # future scan, and a literal here would be a finding about the linter.
    D, I = "-", "i"
    fixtures = {
        "assoc-array":      "declare " + D + "A m",
        "mapfile":          "mapfile " + D + "t arr < f",
        "case-expansion":   "echo ${v^^}",
        "globstar":         "shopt " + D + "s globstar",
        "gnu-timeout":      "timeout 5 sleep 1",
        "pcre-grep":        "grep " + D + "P 'x' f",
        "sed-in-place":     "sed " + D + I + " 's/a/b/' f",
        "gnu-find":         "find . " + D + "printf '%p'",
        "readlink-f":       "readlink " + D + "f /x",
        "gnu-date":         "date " + D + "d yesterday",
        "gnu-stat":         "stat " + D + "c '%s' f",
        "gnu-base64-wrap":  "base64 " + D + "w 0 f",
    }
    declared = {t[0] for t in tokens}
    missing_fixture = declared - set(fixtures)
    if missing_fixture:
        ok = False
        print(f"  ✗ token(s) with no must-fail fixture: {sorted(missing_fixture)}")
    for tok_id, snippet in fixtures.items():
        if tok_id not in declared:
            continue
        hits = {f.token for f in scan_text(snippet, tokens)}
        if tok_id in hits:
            print(f"  ✓ caught: {tok_id}")
        else:
            ok = False
            print(f"  ✗ MISSED: {tok_id} — fixture {snippet!r} produced {sorted(hits)}")

    # Anti-flood companions. A linter that fires on the shimmed form, on prose,
    # or on a sentinel-marked line would be turned off within a day.
    clean = [
        ("shimmed timeout",        '_rc_timeout 5 sleep 1'),
        ("shimmed pcre match",     '_rc_pcre_match "$pat" "$f"'),
        ("shimmed upper",          'u="$(_rc_upper "$v")"'),
        ("a comment naming a banned token", "# never use " + D + "P here; it is GNU-only"),
        ("sentinel-marked line",   "grep " + D + "P 'x' f  # noport: documented example"),
        ("portable read loop",     'while IFS= read -r l; do :; done < f'),
        ("a plain word 'timeout'", 'echo "the timeout was reached"'),
        ("stat with no -c",        "stat " + D + "f '%z' f"),
    ]
    for label, snippet in clean:
        hits = scan_text(snippet, tokens)
        if not hits:
            print(f"  ✓ clean:  {label}")
        else:
            ok = False
            print(f"  ✗ FLOODED on {label}: {[h.token for h in hits]}")

    # An empty / token-less table must fail closed, never pass vacuously.
    with tempfile.TemporaryDirectory() as tmp:
        empty = Path(tmp) / "empty.json"
        empty.write_text('{"tokens": []}', encoding="utf-8")
        try:
            load_tokens(empty)
            ok = False
            print("  ✗ MISSED: a token-less table was accepted instead of failing closed")
        except SystemExit:
            print("  ✓ caught: a token-less table fails closed")

    print("\nteeth verified" if ok else "\nTEETH BROKEN")
    return 0 if ok else 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="repo root to scan")
    ap.add_argument(
        "--report-only",
        action="store_true",
        help="print findings but always exit 0 (the M5 dry-run posture)",
    )
    ap.add_argument("--self-test", action="store_true", help="prove the linter's teeth")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    tokens = load_tokens()
    findings = scan_repo(Path(args.root), tokens)
    if findings:
        print(
            f"portability-lint: {len(findings)} finding(s) — these break on a stock "
            "macOS toolchain, usually SILENTLY",
            file=sys.stderr,
        )
        for f in findings:
            print(f.render(), file=sys.stderr)
        print(
            "\n  Route through plugins/ravenclaude-core/hooks/_portable.sh, or mark a "
            "deliberate occurrence with a trailing `# noport` comment.",
            file=sys.stderr,
        )
        return 0 if args.report_only else 2

    n = len(scoped_files(Path(args.root)))
    print(f"portability-lint: {n} scoped file(s) clean against {len(tokens)} banned tokens")
    return 0


if __name__ == "__main__":
    sys.exit(main())
