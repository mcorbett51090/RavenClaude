#!/usr/bin/env python3
"""
a11y_lint.py -- report-regeneration a11y gate: a stdlib, machine-checkable WCAG-subset
linter over an output HTML deliverable.

This is the HTML **a11y floor** the honest guarantee (../../knowledge/core-architecture-spec.md
sec 1, sec 7 of the FORGE plan) explicitly scopes: automated tooling covers only the
machine-checkable ~30-50% of WCAG. This linter is that floor -- NOT a conformance claim.
Everything a machine cannot decide (alt-text QUALITY, reading-order SENSE, plain-language,
color-independent meaning, complex-table header SENSE) is emitted as `manual_residue`, never
silently claimed as passed. An empty manual-residue section would itself be an over-claim.

It is deliberately a stdlib linter, not Playwright + axe-core: the plan scopes axe-core/veraPDF
as a *later* Tier-B upgrade (§7, §8). This gate runs in Tier-A (stdlib, CI-affordable, no
network, no browser) so a11y regressions are caught on every PR; the browser-based gate is a
strict superset added later.

What it CHECKS (the machine-decidable WCAG floor):

  BLOCKING (an unambiguous WCAG failure a machine can decide with no judgment):
    * img-alt       (WCAG 1.1.1) -- a non-decorative <img> with no `alt` attribute and no
                                     accessible-name fallback (role=presentation/none,
                                     aria-hidden=true, aria-label/-labelledby, title).
    * html-lang     (WCAG 3.1.1) -- <html> with no non-empty `lang`.
    * link-name     (WCAG 2.4.4) -- an <a href> with no accessible name (no text, no
                                     aria-label/-labelledby/title, no child <img alt>).
    * button-name   (WCAG 4.1.2) -- a <button> / input[type in button,submit,reset] with
                                     no accessible name.
    * control-label (WCAG 1.3.1) -- a form control (<input> not hidden/button-like, <select>,
                                     <textarea>) with no associated <label>, aria-label/
                                     -labelledby, or title.
    * table-headers (WCAG 1.3.1) -- a <table> carrying <td> data cells but ZERO <th> headers.

  ADVISORY -> manual residue (a machine can FLAG the candidate; a human confirms):
    * th-scope      (WCAG 1.3.1) -- a <th> in a data table missing both `scope` and `headers`
                                     (simple tables can be fine without it -- flagged, not failed).
    * heading-order (WCAG 1.3.1) -- a heading that skips a level going deeper (h2 -> h4), or a
                                     first heading that is not <h1> (occasionally intentional).

The gate FAILs iff at least one BLOCKING violation is found; else it PASSes with a non-empty
manual-residue checklist. This sub-receipt is folded into `report-qa-gate` (a BLOCKING a11y
violation -> the assembled verdict FAILs; the manual residue -> the reviewer checklist).

This catches seeded defect **D3** (missing alt-text -- scripts/seed_defects.py::inject_D3 strips
`alt` from #chart-region-mix, a non-decorative chart image) as a crisp img-alt BLOCK.

Usage:
    python3 a11y_lint.py --html <output.html> [--format json|text] [--pretty]
    python3 a11y_lint.py --version

Exit codes:
    0 -- gate == PASS (no blocking violation; manual residue still emitted)
    1 -- gate == FAIL (>= 1 blocking violation)
    2 -- usage / path-guard / I/O error (message on stderr + a best-effort JSON error object
         on stdout, mirroring qa_gate.py / seed_defects.py's `_emit_error`)

Design constraints (binding): stdlib only (argparse, html.parser, json, sys, pathlib). No
network, no subprocess, no third-party imports (no axe-core / Playwright -- that is the Tier-B
upgrade). Path-guarded: --html must resolve to a real regular file; NUL bytes rejected. Python
3.9.6 target: `from __future__ import annotations`; no `X | Y` unions, no `match` statements.
"""
from __future__ import annotations

import argparse
import html.parser
import json
import sys
from pathlib import Path

GATE_VERSION = "1.0.0"
SCHEMA = "report-regeneration/a11y-gate@1"

# HTML void elements: html.parser fires handle_starttag with no matching handle_endtag, so the
# tree builder must not push them on the open-element stack.
VOID_ELEMENTS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})

# Form controls that require a programmatic label. `input` is special-cased on its `type`.
_LABELABLE = frozenset({"input", "select", "textarea"})
# input types that are NOT labelable form fields (buttons carry their own name; hidden is not UI).
_NON_LABELABLE_INPUT_TYPES = frozenset({"hidden", "button", "submit", "reset", "image"})
_BUTTON_INPUT_TYPES = frozenset({"button", "submit", "reset", "image"})
_HEADINGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}

# The human-WCAG residue -- the ~30-50% of WCAG that a structural linter (or axe-core/veraPDF)
# cannot judge because it requires human sense-making. Emitted on EVERY run, PASS included: a11y
# is only ever partially auto-covered, so an empty residue would itself be an over-claim
# (core-architecture-spec.md sec 1 honest guarantee; §7 of the FORGE plan).
MANUAL_WCAG_RESIDUE = [
    "Alt-text QUALITY (WCAG 1.1.1) -- presence is machine-checked here; whether each alt "
    "text accurately and usefully DESCRIBES its image's informational content is human-judged.",
    "Reading-order SENSE (WCAG 1.3.2) -- the DOM order exists and is walkable, but whether it "
    "matches the visually intended reading order for a screen-reader user is human-judged.",
    "Plain-language / cognitive load (WCAG 3.1.5) -- reading level, jargon, and abbreviation "
    "expansion are not machine-decidable at this floor.",
    "Heading-hierarchy MEANING (WCAG 1.3.1) -- levels are checked for skips here; whether they "
    "reflect the document's actual semantic structure is human-judged.",
    "Color-independent meaning (WCAG 1.4.1) -- where color conveys information (a red/green KPI), "
    "whether the same information is ALSO conveyed via text/pattern/icon is human-judged. "
    "(Contrast RATIOS also need a rendered-CSS pass -- the Tier-B axe/veraPDF upgrade, not this "
    "stdlib floor.)",
    "Complex-table header association SENSE (WCAG 1.3.1) -- for merged/nested headers, whether "
    "header/id or scope associations LOGICALLY match is human-judged beyond schema validity.",
    "Non-text-media equivalents (WCAG 1.2.x) -- captions/transcripts for embedded audio/video, "
    "and a real long-description for any complex chart beyond a one-line alt.",
    "Focus order + keyboard operability (WCAG 2.1.1, 2.4.3) for any interactive element -- "
    "outside the static-DOM scope this linter covers.",
    "Overall substantive accessibility -- this gate proves only the machine-checkable floor; it "
    "never claims the whole report is accessible (the honest guarantee).",
]


class A11yLintError(Exception):
    """Raised for any path-guard / I/O failure (exit 2)."""


# ---- path guard (mirrors harness.py's safe_read_path: real regular file, reject NUL) ----

def safe_read_path(raw: str) -> Path:
    if not raw or "\x00" in raw:
        raise A11yLintError("empty or NUL-bearing path")
    if ".." in Path(raw).parts:
        raise A11yLintError(f"path traversal ('..') is not allowed: {raw!r}")
    try:
        resolved = Path(raw).resolve()
    except (OSError, RuntimeError) as exc:
        raise A11yLintError(f"cannot resolve path {raw!r}: {exc}") from exc
    if not resolved.exists():
        raise A11yLintError(f"input file not found: {raw!r} (resolved {resolved})")
    if not resolved.is_file():
        raise A11yLintError(f"not a regular file: {raw!r} (resolved {resolved})")
    return resolved


# ---- lightweight HTML tree (stdlib html.parser) ----

class _Node:
    __slots__ = ("tag", "attr", "children", "parent")

    def __init__(self, tag: str, attrs) -> None:
        self.tag = tag
        # last-writer-wins on duplicate attrs, None value -> "" (a bare attribute)
        self.attr = {(k or "").lower(): (v if v is not None else "") for k, v in attrs}
        self.children = []  # list of _Node | str (str == text node)
        self.parent = None


class _TreeBuilder(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("#document", [])
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs) -> None:
        node = _Node(tag, attrs)
        node.parent = self.stack[-1]
        self.stack[-1].children.append(node)
        if tag not in VOID_ELEMENTS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs) -> None:
        node = _Node(tag, attrs)
        node.parent = self.stack[-1]
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag) -> None:
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return
        # no matching open tag -- tolerate (lenient HTML)

    def handle_data(self, data) -> None:
        self.stack[-1].children.append(data)


def parse_html(text: str) -> _Node:
    builder = _TreeBuilder()
    builder.feed(text)
    builder.close()
    return builder.root


def iter_elements(node: _Node):
    for child in node.children:
        if isinstance(child, _Node):
            yield child
            yield from iter_elements(child)


def text_of(node: _Node) -> str:
    out = []

    def rec(n) -> None:
        if isinstance(n, str):
            out.append(n)
        elif isinstance(n, _Node):
            for c in n.children:
                rec(c)

    rec(node)
    return "".join(out)


def _node_label(node: _Node) -> str:
    """A short, stable, human-legible identifier for a node in violation evidence."""
    ident = node.attr.get("id")
    if ident:
        return f"{node.tag}#{ident}"
    cls = node.attr.get("class")
    if cls:
        return f"{node.tag}.{cls.split()[0]}"
    return f"<{node.tag}>"


def _has_accessible_name(node: _Node) -> bool:
    """True if `node` has a machine-detectable accessible name: non-whitespace text content,
    an aria-label / aria-labelledby / title, or (for a link/button) a descendant <img alt>."""
    if text_of(node).strip():
        return True
    for a in ("aria-label", "aria-labelledby", "title"):
        if node.attr.get(a, "").strip():
            return True
    for el in iter_elements(node):
        if el.tag == "img" and el.attr.get("alt", "").strip():
            return True
    return False


def _is_decorative_image(node: _Node) -> bool:
    """An <img> explicitly marked decorative / removed from the a11y tree is exempt from
    needing a name (WCAG 1.1.1's decorative branch)."""
    if node.attr.get("role", "").strip().lower() in ("presentation", "none"):
        return True
    if node.attr.get("aria-hidden", "").strip().lower() == "true":
        return True
    return False


def _violation(rule, wcag, impact, blocking, node_label, detail) -> dict:
    return {
        "rule": rule, "wcag": wcag, "impact": impact, "blocking": blocking,
        "node": node_label, "detail": detail,
    }


# ---- the checks ----

def check_html_lang(root: _Node, violations: list) -> None:
    html_els = [el for el in iter_elements(root) if el.tag == "html"]
    if not html_els:
        return  # a fragment with no <html> -- not this check's concern
    lang = html_els[0].attr.get("lang", "").strip()
    if not lang:
        violations.append(_violation(
            "html-lang", "3.1.1", "serious", True, "<html>",
            "the root <html> element has no non-empty `lang` attribute; a screen reader "
            "cannot select the correct pronunciation rules",
        ))


def check_images(root: _Node, violations: list, counts: dict) -> None:
    for el in iter_elements(root):
        if el.tag != "img":
            continue
        counts["images"] += 1
        if "alt" in el.attr:
            # alt present (even empty == intentionally decorative) -> passes the floor rule.
            continue
        if _is_decorative_image(el):
            continue
        if any(el.attr.get(a, "").strip() for a in ("aria-label", "aria-labelledby", "title")):
            continue
        violations.append(_violation(
            "img-alt", "1.1.1", "critical", True, _node_label(el),
            "a non-decorative <img> has NO `alt` attribute and no accessible-name fallback "
            "(role=presentation/none, aria-hidden, aria-label/-labelledby, title). A decorative "
            "image must declare `alt=\"\"`; an informative one must describe its content.",
        ))


def check_links(root: _Node, violations: list) -> None:
    for el in iter_elements(root):
        if el.tag != "a":
            continue
        if not el.attr.get("href", "").strip():
            continue  # an anchor with no href is not an interactive link
        if not _has_accessible_name(el):
            violations.append(_violation(
                "link-name", "2.4.4", "serious", True, _node_label(el),
                "a link (<a href>) has no accessible name -- no text, aria-label/-labelledby, "
                "title, or child <img alt>; it is announced only as 'link'",
            ))


def check_buttons(root: _Node, violations: list) -> None:
    for el in iter_elements(root):
        is_button = el.tag == "button"
        is_input_button = (
            el.tag == "input"
            and el.attr.get("type", "").strip().lower() in _BUTTON_INPUT_TYPES
        )
        if not (is_button or is_input_button):
            continue
        if is_input_button:
            # a button-like input names itself via `value` (or aria-label / title / alt for image)
            has_name = bool(
                el.attr.get("value", "").strip()
                or el.attr.get("aria-label", "").strip()
                or el.attr.get("aria-labelledby", "").strip()
                or el.attr.get("title", "").strip()
                or el.attr.get("alt", "").strip()
            )
        else:
            has_name = _has_accessible_name(el)
        if not has_name:
            violations.append(_violation(
                "button-name", "4.1.2", "critical", True, _node_label(el),
                "a button has no accessible name (no text / value / aria-label / title); it is "
                "announced only as 'button'",
            ))


def _control_has_label(root: _Node, ctrl: _Node) -> bool:
    if any(ctrl.attr.get(a, "").strip() for a in ("aria-label", "aria-labelledby", "title")):
        return True
    ctrl_id = ctrl.attr.get("id", "").strip()
    if ctrl_id:
        for el in iter_elements(root):
            if el.tag == "label" and el.attr.get("for", "").strip() == ctrl_id:
                return True
    # wrapping <label> ancestor
    parent = ctrl.parent
    while parent is not None and parent.tag != "#document":
        if parent.tag == "label":
            return True
        parent = parent.parent
    return False


def check_form_controls(root: _Node, violations: list) -> None:
    for el in iter_elements(root):
        if el.tag not in _LABELABLE:
            continue
        if el.tag == "input":
            itype = el.attr.get("type", "text").strip().lower()
            if itype in _NON_LABELABLE_INPUT_TYPES:
                continue
        if not _control_has_label(root, el):
            violations.append(_violation(
                "control-label", "1.3.1", "critical", True, _node_label(el),
                f"a <{el.tag}> form control has no programmatic label (no <label for>, wrapping "
                "<label>, aria-label/-labelledby, or title)",
            ))


def check_tables(root: _Node, violations: list, counts: dict) -> None:
    for el in iter_elements(root):
        if el.tag != "table":
            continue
        counts["tables"] += 1
        ths = [d for d in iter_elements(el) if d.tag == "th"]
        tds = [d for d in iter_elements(el) if d.tag == "td"]
        if tds and not ths:
            violations.append(_violation(
                "table-headers", "1.3.1", "serious", True, _node_label(el),
                "a data <table> (it has <td> cells) declares ZERO <th> header cells; screen "
                "readers cannot associate data with headers",
            ))
            continue
        # advisory: a <th> in a data table missing both scope and headers
        for th in ths:
            if not (th.attr.get("scope", "").strip() or th.attr.get("headers", "").strip()):
                violations.append(_violation(
                    "th-scope", "1.3.1", "moderate", False, _node_label(el),
                    "a <th> is missing both `scope` and `headers`; for a simple table this may "
                    "be fine, but the header/data association is not machine-explicit -- confirm",
                ))
                break  # one advisory per table is enough signal


def check_heading_order(root: _Node, violations: list) -> None:
    levels = [_HEADINGS[el.tag] for el in iter_elements(root) if el.tag in _HEADINGS]
    if not levels:
        return
    if levels[0] != 1:
        violations.append(_violation(
            "heading-order", "1.3.1", "moderate", False, f"<h{levels[0]}>",
            f"the first heading is <h{levels[0]}>, not <h1>; confirm the document's heading "
            "hierarchy starts at the top level",
        ))
    prev = levels[0]
    for lvl in levels[1:]:
        if lvl > prev + 1:
            violations.append(_violation(
                "heading-order", "1.3.1", "moderate", False, f"<h{lvl}>",
                f"heading level jumps from <h{prev}> to <h{lvl}>, skipping level(s); a skipped "
                "level can disorient screen-reader navigation -- confirm it is intentional",
            ))
        prev = lvl


# ---- assemble the sub-receipt ----

def lint_html(html_text: str) -> dict:
    """Run every check over `html_text` and return the a11y sub-receipt dict. Never raises on
    malformed HTML (html.parser is lenient) -- only path/IO guards raise."""
    root = parse_html(html_text)
    violations: list = []
    counts = {"images": 0, "tables": 0}

    check_html_lang(root, violations)
    check_images(root, violations, counts)
    check_links(root, violations)
    check_buttons(root, violations)
    check_form_controls(root, violations)
    check_tables(root, violations, counts)
    check_heading_order(root, violations)

    blocking = [v for v in violations if v["blocking"]]
    advisory = [v for v in violations if not v["blocking"]]
    gate = "FAIL" if blocking else "PASS"

    # manual residue = the unconditional WCAG floor note + each advisory violation flagged
    # for human confirmation. NEVER empty (the floor note is unconditional).
    manual_residue = list(MANUAL_WCAG_RESIDUE)
    for v in advisory:
        manual_residue.append(f"[{v['rule']} @ {v['node']}] {v['detail']}")

    return {
        "schema": SCHEMA,
        "gate_version": GATE_VERSION,
        "gate": gate,
        "coverage": (
            "machine-checkable WCAG floor only (~30-50% of WCAG, community order-of-magnitude); "
            "the remainder is manual residue, never claimed as passed. Contrast ratios + rendered "
            "layout need the Tier-B axe-core/veraPDF upgrade, not this stdlib floor."
        ),
        "counts": {
            "blocking": len(blocking),
            "advisory": len(advisory),
            "images": counts["images"],
            "tables": counts["tables"],
        },
        "violations": violations,
        "manual_residue": manual_residue,
    }


def lint_file(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise A11yLintError(f"could not read HTML file: {exc}") from exc
    return lint_html(text)


# ---- CLI ----

def _emit_error(message: str) -> None:
    print(json.dumps({"schema": SCHEMA, "ok": False, "error": message}), file=sys.stdout)
    print(f"[error] {message}", file=sys.stderr)


def _print_text(receipt: dict) -> None:
    print(f"report-a11y-gate v{GATE_VERSION} -- machine-checkable WCAG floor")
    print(f"  gate: {receipt['gate']}")
    c = receipt["counts"]
    print(f"  blocking violations: {c['blocking']} | advisory: {c['advisory']} "
          f"| images scanned: {c['images']} | tables scanned: {c['tables']}")
    if receipt["violations"]:
        print("  violations:")
        for v in receipt["violations"]:
            tier = "BLOCK" if v["blocking"] else "advisory"
            print(f"    [{tier}] {v['rule']} (WCAG {v['wcag']}, {v['impact']}) @ {v['node']}")
            print(f"           {v['detail']}")
    print(f"  manual residue ({len(receipt['manual_residue'])} item(s)) -- human review REQUIRED "
          "regardless of gate (this is only the ~30-50% floor):")
    for item in receipt["manual_residue"]:
        print(f"    - {item}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="a11y_lint.py",
        description="Machine-checkable WCAG-subset a11y linter over an output HTML deliverable "
                    "(the stdlib Tier-A a11y floor for report-regeneration).",
    )
    p.add_argument("--html", metavar="PATH", help="path to the output HTML to lint")
    p.add_argument("--format", dest="out_format", choices=["json", "text"], default="text",
                   help="output format (default: text)")
    p.add_argument("--pretty", action="store_true", help="pretty-print the JSON sub-receipt")
    p.add_argument("--version", action="store_true", help="print the gate version and exit")
    return p


def main(argv) -> int:
    args = build_parser().parse_args(argv)
    if args.version:
        print(GATE_VERSION)
        return 0
    if not args.html:
        build_parser().print_usage(sys.stderr)
        _emit_error("--html is required (or pass --version)")
        return 2
    try:
        path = safe_read_path(args.html)
        receipt = lint_file(path)
    except A11yLintError as exc:
        _emit_error(str(exc))
        return 2

    if args.out_format == "json":
        print(json.dumps(receipt, indent=2 if args.pretty else None))
    else:
        _print_text(receipt)
    return 1 if receipt["gate"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
