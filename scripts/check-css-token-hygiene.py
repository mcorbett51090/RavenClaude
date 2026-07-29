#!/usr/bin/env python3
"""check-css-token-hygiene.py — Gate 174: design-token misuse that renders unreadable.

WHY THIS EXISTS. A browser-driven audit of both dashboard surfaces (2026-07-29) found
24 real defects. Three classes accounted for most of them, all invisible to every
existing gate because the CSS is *valid* and the page *renders* — it just renders
something a person cannot read:

  1. A HAIRLINE token used as a foreground colour. `--border` is `rgba(255,255,255,.07)`.
     Two rules used it as `color:` — the word "off" in the command-review summary and
     the review-scales icon's off state — putting the review state you most need to
     notice at **1.17:1**. Nothing errors; the text is simply not there.

  2. A THEME-BLIND literal on a themed fill. `background: var(--accent); color: #fff`
     measures **1.95:1**; on `var(--danger)` in dark theme, `color: white` is **2.76:1**.
     A hardcoded literal also cannot follow the light/dark token swap at all, so it is
     wrong in at least one theme by construction. Six controls carried this, including
     a primary action and an alert banner. The house pairing is `var(--bg)` on a themed
     fill (see `.seg-label:checked`), which measures 10.3:1 dark / 5.0:1 light.

  3. `repeat(auto-fit, minmax(<N>px, 1fr))` with a bare track minimum. A track minimum
     cannot shrink below itself, so a container narrower than N overflows and the whole
     document scrolls sideways — hiding the nav and every other panel. `minmax(320px,1fr)`
     in a 287px container did this at 375px; `minmax(340px,1fr)` did it at 320px.
     `min(<N>px, 100%)` is a no-op whenever the container is wider than N, so requiring
     it costs nothing and removes the class.

  4. A generated dashboard surface with no bare-`a` colour rule. The shipped
     `dashboard.html` had none, so every inline link in its prose fell back to the
     browser default `#0000EE` — about **2:1** on its dark surfaces. The dev portal hid
     this because the *shell* supplies a link colour, which is the trap: the embedding
     surface can supply defaults the embedded, shipped one lacks.

SCOPE, STATED HONESTLY. This gate is a static text lint over CSS *sources*. It cannot
compute a contrast ratio, and it deliberately does not try — a general "is this
readable?" check needs a browser, and a hand-rolled approximation of one is how the
audit that motivated this gate produced 3,337 findings of which ~99% were false
(see docs/best-practices/validating-a-measuring-instrument.md). What it does instead is
catch the small number of token-misuse SHAPES that are wrong by construction, where no
measurement is needed to know the answer. Rules 1-3 scan sources; rule 4 checks the two
generated dashboard outputs, where arbitrary prose with inline links makes a bare-`a`
colour rule a genuine invariant.

Rule 4 is deliberately NOT generalised to every HTML template. Tried and rejected: a
"template has links but no `a` rule" heuristic flagged `marketing-page.html`, whose six
links are all covered by `.nav a` and `.btn`. A checker that cries wolf gets ignored —
the same reasoning `storage-placement-nudge.sh` records in its own header.

ESCAPE HATCH. Put `token-hygiene-ok` in a comment on the offending line. Mirrors the
`placement-ok` / `delegation-nudge-ok` convention already used in this repo.

Usage:
  python3 scripts/check-css-token-hygiene.py              # lint the repo
  python3 scripts/check-css-token-hygiene.py --must-fail  # teeth: fixtures must be caught
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# CSS sources: the generators and hand-authored templates. Generated *outputs* are
# derived, so linting them would double-report the same source line.
SOURCE_GLOBS = [
    "scripts/generate-*.py",
    "scripts/_index_dashboard_template.py",
    "plugins/*/templates/**/*.html",
    "plugins/*/dashboard-assets/*.css",
]

# Rule 4 applies to the generated dashboard surfaces only — see the header.
LINK_RULE_SURFACES = ["index.html", "plugins/*/dashboard.html"]

OPT_OUT = "token-hygiene-ok"

# ── rule 1: a hairline/border token as a FOREGROUND colour ────────────────────
# `(?<![-\w])color` so `border-color:` / `outline-color:` / `caret-color:` /
# `text-decoration-color:` are not matched — only the `color` property itself.
R_HAIRLINE = re.compile(r"(?<![-\w])color:\s*var\(\s*--(?:rc-)?border(?:-strong)?\s*[,)]")

# ── rule 2: theme-blind literal alongside a themed fill, in the same declaration ──
_LITERAL = r"(?:#fff(?:fff)?|#000(?:000)?|white|black)\b"
_THEMED_FILL = r"background(?:-color)?:\s*var\(\s*--(?:rc-)?(?:accent|danger|warn|teal|ok)"
R_BLIND_A = re.compile(_THEMED_FILL + r"[^;{}]*;[^{}]*?(?<![-\w])color:\s*" + _LITERAL)
R_BLIND_B = re.compile(r"(?<![-\w])color:\s*" + _LITERAL + r"[^{}]*?" + _THEMED_FILL)

# ── rule 3: bare track minimum in an auto-fit/auto-fill grid ──────────────────
R_MINMAX = re.compile(r"repeat\(\s*auto-(?:fit|fill)\s*,\s*minmax\(\s*\d+px")


def _iter_sources() -> list[Path]:
    out: list[Path] = []
    for pat in SOURCE_GLOBS:
        out.extend(sorted(ROOT.glob(pat)))
    return [p for p in out if p.is_file()]


def scan_text(text: str, label: str) -> list[str]:
    """Return one finding string per offending line."""
    findings = []
    for i, line in enumerate(text.splitlines(), 1):
        if OPT_OUT in line:
            continue
        if R_HAIRLINE.search(line):
            findings.append(
                f"{label}:{i}: a hairline token (--border) is used as a foreground "
                f"colour — it is ~7% alpha, so this renders at ~1.2:1. Use --muted."
            )
        if R_BLIND_A.search(line) or R_BLIND_B.search(line):
            findings.append(
                f"{label}:{i}: a hardcoded #fff/#000/white/black sits on a themed fill "
                f"(var(--accent|danger|warn|teal|ok)) — 1.95:1 on accent, 2.76:1 on "
                f"dark-theme danger, and it cannot follow the theme swap. Use var(--bg)."
            )
        if R_MINMAX.search(line):
            findings.append(
                f"{label}:{i}: repeat(auto-fit/auto-fill, minmax(<N>px, ...)) with a bare "
                f"track minimum — a container narrower than N overflows and scrolls the "
                f"whole page sideways. Use minmax(min(<N>px, 100%), ...)."
            )
    return findings


def _has_bare_link_colour(html: str) -> bool:
    """Does a bare `a` selector set a colour anywhere in this document?

    Looks for a selector list containing a standalone `a` (not `.nav a`, not `a.btn`)
    whose block declares `color`.

    Two things this got wrong on the first write, both worth keeping written down:
      - It scanned the whole document. These pages carry large inline scripts whose
        braces pair up into plausible-looking "rules", which can only ever invent a
        rule that is not there — i.e. hide a real defect. Only <style> is scanned now.
      - It did not strip CSS comments, so `[^{}]*` before a rule swallowed the comment
        prose ABOVE it and the selector became "…so something is a link. Scoped to" —
        which is why it reported dashboard.html as having no link rule when it has one.
    """
    styles = re.findall(r"<style[^>]*>(.*?)</style>", html, re.S | re.I)
    if not styles:
        return False
    for css in styles:
        css = re.sub(r"/\*.*?\*/", " ", css, flags=re.S)
        for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", css):
            selectors, body = m.group(1), m.group(2)
            if not re.search(r"(?<![-\w])color\s*:", body):
                continue
            for sel in selectors.split(","):
                if re.fullmatch(r"\s*a\s*(?::link|:visited)?\s*", sel):
                    return True
    return False


def run() -> int:
    findings: list[str] = []
    scanned = 0
    for p in _iter_sources():
        scanned += 1
        findings += scan_text(p.read_text(encoding="utf-8", errors="replace"), str(p.relative_to(ROOT)))

    surfaces = 0
    for pat in LINK_RULE_SURFACES:
        for p in sorted(ROOT.glob(pat)):
            if not p.is_file():
                continue
            surfaces += 1
            html = p.read_text(encoding="utf-8", errors="replace")
            if OPT_OUT in html:
                continue
            if not _has_bare_link_colour(html):
                findings.append(
                    f"{p.relative_to(ROOT)}: no bare `a {{ color: ... }}` rule — every inline "
                    f"link in this document's prose falls back to the browser default "
                    f"#0000EE, which is ~2:1 on a dark surface. This exact defect shipped "
                    f"in dashboard.html and was masked by the portal shell supplying a "
                    f"link colour the standalone page lacked."
                )

    print(f"css token hygiene: {scanned} source file(s), {surfaces} generated surface(s)")
    if findings:
        print(f"\n{len(findings)} finding(s):")
        for f in findings:
            print("  ✗ " + f)
        print(f"\n(silence one with a `{OPT_OUT}` comment on the line, if it is genuinely correct)")
        return 1
    print("  ✓ no token-misuse shapes found")
    return 0


# ── teeth: fixtures that MUST be caught, and correct code that must NOT be ─────
_BAD = [
    ('.x { color: var(--border); }', "hairline as foreground"),
    ('.x { color: var(--rc-border-strong); }', "hairline variant as foreground"),
    ('.x { background: var(--accent); color: #fff; }', "literal on themed fill"),
    ('.x { color: white; background: var(--danger); }', "literal before themed fill"),
    ('.x { background-color: var(--rc-warn); color: #000000; }', "long-form both"),
    ('.g { grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }', "bare track min"),
    ('.g { grid-template-columns: repeat(auto-fill, minmax(340px,1fr)); }', "bare track min, no space"),
]
_GOOD = [
    ('.x { border-color: var(--border); }', "border-color is not a foreground"),
    ('.x { outline-color: var(--border); }', "outline-color is not a foreground"),
    ('.x { text-decoration-color: var(--rc-border); }', "decoration-color is not a foreground"),
    ('.x { color: var(--muted); }', "the correct token"),
    ('.x { background: var(--accent); color: var(--bg); }', "the house pairing"),
    ('.g { grid-template-columns: repeat(auto-fit, minmax(min(320px, 100%), 1fr)); }', "guarded"),
    ('.g { grid-template-columns: minmax(180px, 240px) 1fr auto; }', "not an auto-fit repeat"),
    ('.x { color: var(--border); } /* token-hygiene-ok */', "opt-out honoured"),
]


def self_test() -> int:
    bad_missed = [(css, why) for css, why in _BAD if not scan_text(css, "fx")]
    good_flagged = [(css, why) for css, why in _GOOD if scan_text(css, "fx")]

    # rule 4 fixtures
    r4_bad = "<style>/* a link */ body{color:#fff} .nav a{color:red}</style><a href=x>y</a>"
    r4_good = "<style>a { color: var(--accent); }</style><a href=x>y</a>"
    r4_ok = (not _has_bare_link_colour(r4_bad)) and _has_bare_link_colour(r4_good)

    print("token-hygiene self-test")
    print(f"  known-bad caught : {len(_BAD) - len(bad_missed)}/{len(_BAD)}")
    print(f"  known-good clean : {len(_GOOD) - len(good_flagged)}/{len(_GOOD)}")
    print(f"  rule 4 bidirectional: {'yes' if r4_ok else 'NO'}")
    for css, why in bad_missed:
        print(f"  ✗ MISSED ({why}): {css}")
    for css, why in good_flagged:
        print(f"  ✗ FALSE POSITIVE ({why}): {css}")
    if bad_missed or good_flagged or not r4_ok:
        print("\nself-test FAILED — the gate does not have the teeth it claims")
        return 1
    print("\nself-test passed (fail-on-bad AND pass-on-good, both directions)")
    return 0


if __name__ == "__main__":
    if "--must-fail" in sys.argv:
        # `audit-gates.sh` teeth half: exit 0 only when every known-bad fixture is
        # caught and every known-good one is left alone.
        sys.exit(self_test())
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.exit(run())
