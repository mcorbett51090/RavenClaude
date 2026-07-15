#!/usr/bin/env python3
"""
svg-report-lint — SVG geometry, legibility, and security linter (Gate 103).

Checks a standalone SVG file for structural soundness and injection vectors.
Stdlib-only (xml.etree.ElementTree + re), no network, exit-coded for CI.

Exit codes:
  0 — clean (no violations)
  1 — one or more violations found
  2 — I/O, parse, or path-rejection error (purity failure: '..' in path,
      path outside the repo root, or file not found/unreadable)

Checks (all → exit 1 on violation):
  (a) viewbox-present      — root <svg> must have a viewBox attribute
  (b) viewbox-sane-aspect  — viewBox width/height ratio must be between 0.05 and 20
  (c) text-min-fontsize    — <text> elements must have font-size >= min_fontsize (default 8)
  (d) no-script            — no <script> element (script injection)
  (e) no-inline-handlers   — no on* event attributes (inline JS)
  (f) no-foreign-object    — no <foreignObject> element (XSS-escalation)
  (g) no-remote-href       — no remote or javascript: href / xlink:href
  (h) no-remote-use        — no <use> referencing a remote URL

Usage:
  python3 lint.py <file.svg> [--min-fontsize N] [--debug]
  python3 lint.py --list-checks
"""


# PEP-604 unions (`X | None`) appear in annotations below. They are evaluated at RUNTIME,
# so on Python 3.9 — which stock macOS ships — this module raises TypeError at import and
# the caller sees a crash, not a lint result. CI runs 3.10+, where it works, which is what
# made this easy to miss. Deferring annotation evaluation costs nothing here: this module
# does no runtime annotation introspection. (2026-07-15)
from __future__ import annotations
import os
import re
import sys
import xml.etree.ElementTree as ET

CHECKS = [
    ("viewbox-present",     "root <svg> missing viewBox attribute — required for responsive scaling"),
    ("viewbox-sane-aspect", "viewBox aspect ratio is outside the 0.05..20 range (may render as a sliver or pillar)"),
    ("text-min-fontsize",   "<text> element has font-size below the minimum (illegible at typical report scale)"),
    ("no-script",           "<script> element in SVG — script injection vector"),
    ("no-inline-handlers",  "on* event attribute in SVG — inline JS event handler vector"),
    ("no-foreign-object",   "<foreignObject> element in SVG — XSS-escalation vector"),
    ("no-remote-href",      "remote or javascript: href/xlink:href in SVG — network call + potential JS"),
    ("no-remote-use",       "<use> referencing a remote URL — network fetch + potential injection"),
]

DEFAULT_MIN_FONTSIZE = 8
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

_RE_ON_ATTR     = re.compile(r"\bon\w+\s*=", re.IGNORECASE)
_RE_REMOTE_HREF = re.compile(
    r"""(?:xlink:)?href\s*=\s*['"]?\s*(?:https?://|javascript:)""",
    re.IGNORECASE,
)


def list_checks() -> None:
    print("Gate 103 — svg-report-lint checks:")
    for key, desc in CHECKS:
        print(f"  [{key}] {desc}")


# ── path safety ───────────────────────────────────────────────────────────────

def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    root = here
    for _ in range(10):
        if os.path.isfile(os.path.join(root, ".repo-layout.json")) or \
           os.path.isfile(os.path.join(root, "AGENTS.md")):
            return root
        parent = os.path.dirname(root)
        if parent == root:
            break
        root = parent
    return os.path.abspath(os.path.join(here, "../../../.."))


def _safe_path(raw: str) -> str:
    """Resolve and validate path; exit 2 on traversal or escape."""
    if ".." in raw:
        print(f"[error] path contains '..': {raw!r}", file=sys.stderr)
        sys.exit(2)
    repo = _repo_root()
    abs_path = os.path.realpath(os.path.join(os.getcwd(), raw))
    if not abs_path.startswith(os.path.realpath(repo)):
        print(f"[error] path escapes repo root: {abs_path!r}", file=sys.stderr)
        sys.exit(2)
    return abs_path


# ── viewBox helpers ───────────────────────────────────────────────────────────

def _parse_viewbox(vb: str):
    """Return (min_x, min_y, width, height) floats or None on parse error."""
    parts = vb.replace(",", " ").split()
    if len(parts) != 4:
        return None
    try:
        return tuple(float(p) for p in parts)
    except ValueError:
        return None


# ── font-size helpers ─────────────────────────────────────────────────────────

_RE_FONTSIZE_ATTR  = re.compile(r"^(\d+(?:\.\d+)?)(px|pt|em|rem|%)?$", re.IGNORECASE)
_RE_FONTSIZE_STYLE = re.compile(
    r"font-size\s*:\s*(\d+(?:\.\d+)?)(px|pt|em|rem|%)?", re.IGNORECASE
)


def _fontsize_px(val_str: str) -> float | None:
    """Convert a font-size string to an approximate px value; None on failure."""
    val_str = val_str.strip()
    m = _RE_FONTSIZE_ATTR.match(val_str)
    if not m:
        return None
    n = float(m.group(1))
    unit = (m.group(2) or "").lower()
    if unit in ("", "px"):
        return n
    if unit == "pt":
        return n * 96 / 72
    if unit in ("em", "rem"):
        return n * 16  # assume 16px default
    return None  # % is context-dependent; skip


def _element_fontsize(elem: ET.Element) -> float | None:
    """Return the effective font-size of a <text> element in px, or None."""
    # Presentation attribute
    fa = elem.get("font-size")
    if fa:
        px = _fontsize_px(fa)
        if px is not None:
            return px
    # Inline style
    style = elem.get("style", "")
    m = _RE_FONTSIZE_STYLE.search(style)
    if m:
        val_str = m.group(1) + (m.group(2) or "")
        px = _fontsize_px(val_str)
        if px is not None:
            return px
    return None


# ── regex-based checks on raw content (catches namespace variants) ────────────

def _check_raw(content: str, violations: list) -> None:
    """Regex-based checks that are robust to namespace variations."""
    if _RE_ON_ATTR.search(content):
        violations.append(("no-inline-handlers", "on* event attribute found in SVG"))
    if _RE_REMOTE_HREF.search(content):
        violations.append(("no-remote-href", "remote or javascript: href/xlink:href found in SVG"))


# ── ElementTree-based checks ──────────────────────────────────────────────────

_SCRIPT_TAGS   = {f"{{{SVG_NS}}}script", "script"}
_FOREIGN_TAGS  = {f"{{{SVG_NS}}}foreignObject", "foreignObject"}
_USE_TAGS      = {f"{{{SVG_NS}}}use", "use"}
_TEXT_TAGS     = {f"{{{SVG_NS}}}text", "text",
                  f"{{{SVG_NS}}}tspan", "tspan",
                  f"{{{SVG_NS}}}tref", "tref"}
_REMOTE_RE     = re.compile(r"^(?:https?://|javascript:)", re.IGNORECASE)


def _check_tree(root: ET.Element, violations: list, min_fontsize: float) -> None:
    """ElementTree-based structural checks."""
    # (a) viewbox-present
    vb = root.get("viewBox") or root.get("viewbox")
    if not vb:
        violations.append(("viewbox-present", "<svg> root has no viewBox attribute"))
    else:
        # (b) viewbox-sane-aspect
        parsed = _parse_viewbox(vb)
        if parsed is not None:
            _, _, w, h = parsed
            if h > 0:
                ratio = w / h
                if ratio < 0.05 or ratio > 20:
                    violations.append((
                        "viewbox-sane-aspect",
                        f"viewBox aspect ratio {ratio:.2f} is outside 0.05..20 "
                        f"(width={w}, height={h})"
                    ))

    for elem in root.iter():
        etag_bare = elem.tag.replace(f"{{{SVG_NS}}}", "").lower()
        etag_full = elem.tag

        # (d) no-script
        if etag_full in _SCRIPT_TAGS or etag_bare == "script":
            violations.append(("no-script", "<script> element found in SVG"))

        # (f) no-foreign-object
        if etag_full in _FOREIGN_TAGS or etag_bare == "foreignobject":
            violations.append(("no-foreign-object", "<foreignObject> element found in SVG"))

        # (g) no-remote-href — resolved-attribute check (entity-decode bypass prevention)
        # ElementTree resolves XML character entities in attribute values during parsing,
        # so &#106;avascript:alert(1) becomes javascript:alert(1) here. This catches
        # entity-encoded schemes that the raw-text regex in _check_raw() cannot see.
        href_resolved = (elem.get(f"{{{XLINK_NS}}}href") or elem.get("href") or "")
        if href_resolved and _REMOTE_RE.match(href_resolved):
            violations.append(("no-remote-href",
                f"<{etag_bare}> href/xlink:href references remote or javascript: URL: "
                f"{href_resolved!r}"))

        # (h) no-remote-use
        if etag_full in _USE_TAGS or etag_bare == "use":
            href = (elem.get(f"{{{XLINK_NS}}}href") or
                    elem.get("href") or "")
            if _REMOTE_RE.match(href):
                violations.append(("no-remote-use",
                    f"<use> references a remote URL: {href!r}"))

        # (c) text-min-fontsize
        if etag_full in _TEXT_TAGS or etag_bare in ("text", "tspan", "tref"):
            fs = _element_fontsize(elem)
            if fs is not None and fs < min_fontsize:
                violations.append((
                    "text-min-fontsize",
                    f"<{etag_bare}> has font-size {fs:.1f}px "
                    f"(minimum {min_fontsize}px)"
                ))


# ── main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    args = sys.argv[1:]
    debug = "--debug" in args
    args = [a for a in args if a != "--debug"]

    if "--list-checks" in args:
        list_checks()
        return 0

    min_fontsize = DEFAULT_MIN_FONTSIZE
    if "--min-fontsize" in args:
        idx = args.index("--min-fontsize")
        if idx + 1 >= len(args):
            print("[error] --min-fontsize requires a numeric argument", file=sys.stderr)
            return 2
        try:
            min_fontsize = float(args[idx + 1])
        except ValueError:
            print(f"[error] --min-fontsize value is not numeric: {args[idx+1]!r}",
                  file=sys.stderr)
            return 2
        args = args[:idx] + args[idx + 2:]

    if not args:
        print("usage: lint.py <file.svg> [--min-fontsize N] [--debug]", file=sys.stderr)
        return 2

    raw_path = args[0]
    abs_path = _safe_path(raw_path)

    if not os.path.isfile(abs_path):
        print(f"[error] file not found: {abs_path!r}", file=sys.stderr)
        return 2

    try:
        content = open(abs_path, encoding="utf-8").read()
    except OSError as exc:
        print(f"[error] cannot read file: {exc}", file=sys.stderr)
        return 2

    violations: list = []

    # Regex pass (robust to namespace variants)
    _check_raw(content, violations)

    # ElementTree pass (structural checks)
    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        print(f"[error] SVG XML parse error: {exc}", file=sys.stderr)
        return 2

    _check_tree(root, violations, min_fontsize)

    if debug:
        print(f"[debug] path={abs_path!r}, min_fontsize={min_fontsize}, "
              f"violations={violations}")

    # Deduplicate (regex pass and tree pass may both catch the same issue)
    seen = set()
    deduped = []
    for key, detail in violations:
        k = (key, detail)
        if k not in seen:
            seen.add(k)
            deduped.append((key, detail))

    if not deduped:
        print(f"[lint] PASS — {raw_path}")
        return 0

    print(f"[lint] FAIL — {raw_path} ({len(deduped)} violation(s)):")
    for key, detail in deduped:
        print(f"  [{key}] {detail}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
