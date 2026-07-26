#!/usr/bin/env python3
"""
rr_anchor.py — the SHARED report-regeneration anchor resolver (stdlib, py3.9-safe).

The one abstraction the whole HTML lane lowers onto. `infer.py` is the anchor PRODUCER; it
emits three anchor shapes for a node's stable identity (core-architecture-spec.md §2 — an
element id / CSS selector, NEVER a char-offset):

    1. element_id            {"kind": "element_id", "value": "kpi-revenue"}       (node carries id=)
    2. simple #id selector   {"kind": "css_selector", "value": "#kpi-revenue"}    (rare; an id in
                             selector clothing)
    3. compound css_selector {"kind": "css_selector",
                             "value": "#sec-exec-summary > h2:nth-of-type(1)"}    (id-less node,
                             anchored at the nearest ancestor that HAS an id, or)
                             {"kind": "css_selector",
                             "value": "html > head:nth-of-type(1) > meta:nth-of-type(1)"} (rooted at
                             the bare document-root tag when no ancestor carries an id)

Before this module the CONSUMERS (`rebind_html.py` stage 3, `report-fidelity-harness/harness.py`
stage 4) only resolved forms (1) and (2) — a compound (3) selector aborted the run. This resolver
closes that gap so every stage resolves the SAME anchor grammar infer produces. It is NOT a full
CSS engine: it supports EXACTLY the grammar `infer._anchor_for()` emits (`tag`, `#id`, and
`" > "`-joined `tag:nth-of-type(n)` descendant steps), and nothing else.

Grammar (a PEG restatement of infer._anchor_for's output):
    anchor      := element_id | selector
    selector    := root_step (" > " step)*
    root_step   := "#" IDENT            # nearest-ancestor-id anchor
                 | TAG                  # the bare document-root element's tag (no nth-of-type)
    step        := TAG ":nth-of-type(" N ")"   # 1-based nth-of-type among same-tag element siblings

What a resolved `Node` gives every consumer:
    - a stable structural identity `path` — the tuple of (tag, nth-of-type) from the document root
      down — so two independently-built trees over the SAME html string agree on which node an
      anchor names (harness masks V2/V3 regions by this; a different tree impl computes the same
      tuple);
    - the exact source-character spans of the open tag / inner content / whole node, so a byte-
      surgeon (rebind) can read+replace inner content or edit the open tag WITHOUT a DOM re-render.

Design constraints (binding): stdlib only (html.parser, xml.parsers.expat, re). Runs on Python
3.9.6 — `from __future__ import annotations`, no PEP-604 `X | Y`, no `match`. No network, no
subprocess, no file I/O (callers pass an html STRING, or — for Office — the `word/document.xml`
string/bytes or the whole `.docx` zip bytes; the zip is opened in-memory, never a path read).
nth-of-type semantics mirror infer._TreeBuilder/_anchor_for EXACTLY (count among same-tag element
siblings, 1-based, document order; void/self-closing elements are counted, text/comments/decls are
not).

── OFFICE (OOXML) extension ──────────────────────────────────────────────────────────────────────
This module ALSO owns the shared OOXML (Office / Word `.docx`) anchor contract that the Office lane
(infer-office producer -> rebind-office -> the Office fidelity harness) lowers onto — the exact
Office analogue of the HTML grammar above, pinned in core-architecture-spec.md §2. See the
"OFFICE / OOXML" section at the bottom of this file for the grammar, the shared indexing rule, and
the body-walk resolver (`ooxml_resolve` / `ooxml_try_resolve` / `ooxml_exists` /
`ooxml_document_path`). The HTML resolver above is untouched by that extension.
"""
from __future__ import annotations

import io
import re
import zipfile
from html.parser import HTMLParser
from typing import Any
from xml.parsers import expat

# Void (self-closing) HTML elements — no end tag, never pushed onto the open-element stack.
# Kept byte-identical to infer._VOID_TAGS / harness.VOID_ELEMENTS so the three trees agree.
_VOID_TAGS = frozenset(
    [
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    ]
)

_STEP_RE = re.compile(r"^([a-zA-Z][\w-]*):nth-of-type\((\d+)\)$")
_IDENT_RE = re.compile(r"^[A-Za-z][\w-]*$")


class AnchorError(Exception):
    """Raised for an unparseable anchor or an anchor that resolves to no node. Never a bare
    IndexError/KeyError — a caller catches exactly this to fall back or fail loudly."""


# ── the element tree (html.parser; records source spans + document order) ─────────────────────

class _El:
    __slots__ = (
        "tag", "attrs", "parent", "children", "type_index",
        "open_start", "open_end", "close_start", "close_end", "is_void",
    )

    def __init__(self, tag: str, attrs: dict[str, str], parent: _El | None) -> None:
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children: list[_El] = []
        self.type_index = 1  # 1-based nth-of-type among same-tag siblings (document order)
        self.open_start = -1
        self.open_end = -1
        self.close_start = -1  # -1 until a matching end tag is seen (or for a void element)
        self.close_end = -1
        self.is_void = False


class _TreeBuilder(HTMLParser):
    """Builds an ordered _El tree AND records each element's source-character spans. Tolerant of
    unclosed/misnested tags (mirrors infer._TreeBuilder): an end tag pops down to its nearest
    matching open element, or is ignored. void/self-closing elements are added as children but
    never pushed (so nth-of-type still counts them, exactly like infer)."""

    def __init__(self, source: str) -> None:
        super().__init__(convert_charrefs=True)
        self._source = source
        # line -> absolute char offset of that line's start (1-based lines, as html.parser reports)
        self._line_starts = [0]
        for line in source.splitlines(keepends=True):
            self._line_starts.append(self._line_starts[-1] + len(line))
        self.root = _El("#document", {}, None)
        self._stack: list[_El] = [self.root]

    def _abs(self) -> int:
        line, col = self.getpos()
        return self._line_starts[line - 1] + col

    def _open(self, tag: str, attrs: list[tuple[str, str | None]]) -> _El:
        parent = self._stack[-1]
        attr_map: dict[str, str] = {}
        for k, v in attrs:
            if k not in attr_map:  # first occurrence wins (HTML5 duplicate-attribute rule)
                attr_map[k] = v if v is not None else ""
        el = _El(tag, attr_map, parent)
        el.type_index = 1 + sum(1 for c in parent.children if c.tag == tag)
        el.open_start = self._abs()
        raw = self.get_starttag_text() or ""
        el.open_end = el.open_start + len(raw)
        parent.children.append(el)
        return el

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        el = self._open(tag, attrs)
        if tag in _VOID_TAGS:
            el.is_void = True
        else:
            self._stack.append(el)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        el = self._open(tag, attrs)  # explicit self-close — never pushed
        el.is_void = True

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self._stack) - 1, 0, -1):  # never pop the synthetic root at index 0
            if self._stack[i].tag == tag:
                closing = self._stack[i]
                closing.close_start = self._abs()
                gt = self._source.find(">", closing.close_start)
                closing.close_end = (gt + 1) if gt != -1 else len(self._source)
                del self._stack[i:]
                return
        # no matching open element — ignore (tolerant, mirrors infer)


def _build_tree(html: str) -> _El:
    builder = _TreeBuilder(html)
    builder.feed(html)
    builder.close()
    return builder.root


def _root_elements(document: _El) -> list[_El]:
    return list(document.children)


# ── the resolved node handed back to every consumer ──────────────────────────────────────────

class Node:
    """A resolved anchor target. Exposes the node's stable structural identity (`path`) and the
    source-character spans a byte-surgeon needs to read/replace content without a DOM re-render."""

    __slots__ = ("_el",)

    def __init__(self, el: _El) -> None:
        self._el = el

    @property
    def tag(self) -> str:
        return self._el.tag

    @property
    def attrs(self) -> dict[str, str]:
        return dict(self._el.attrs)

    @property
    def element_id(self) -> str | None:
        return self._el.attrs.get("id")

    @property
    def is_void(self) -> bool:
        # A void element, OR a paired element whose close tag was never seen (best-effort).
        return self._el.is_void or self._el.close_start == -1

    @property
    def is_paired(self) -> bool:
        return not self.is_void

    @property
    def open_start(self) -> int:
        return self._el.open_start

    @property
    def open_end(self) -> int:
        return self._el.open_end

    @property
    def inner_start(self) -> int:
        """Char offset where inner content begins (== end of the open tag). Meaningless for a
        void element (inner_start == inner_end == open_end there)."""
        return self._el.open_end

    @property
    def inner_end(self) -> int:
        """Char offset where inner content ends (== start of the close tag). For a void element
        this collapses to open_end (empty inner)."""
        return self._el.close_start if self._el.close_start != -1 else self._el.open_end

    @property
    def outer_start(self) -> int:
        return self._el.open_start

    @property
    def outer_end(self) -> int:
        return self._el.close_end if self._el.close_end != -1 else self._el.open_end

    @property
    def path(self) -> tuple[tuple[str, int], ...]:
        """The stable structural identity: (tag, nth-of-type) from the document root down. Two
        html.parser trees over the SAME source agree on this tuple, so a consumer with its own
        tree (harness) can mask/locate the exact node an anchor names."""
        steps: list[tuple[str, int]] = []
        cur: _El | None = self._el
        while cur is not None and cur.tag != "#document":
            steps.append((cur.tag, cur.type_index))
            cur = cur.parent
        return tuple(reversed(steps))

    def open_tag_text(self, html: str) -> str:
        return html[self._el.open_start:self._el.open_end]

    def inner_text(self, html: str) -> str:
        if self.is_void:
            return ""
        return html[self.inner_start:self.inner_end]

    def outer_text(self, html: str) -> str:
        return html[self.outer_start:self.outer_end]


# ── anchor normalization + parsing (EXACTLY infer's grammar, nothing more) ────────────────────

def _normalize_anchor(anchor: Any) -> tuple[str, str]:
    """Return ('id', value) or ('selector', value). Accepts an anchor dict ({'kind','value'}) or a
    bare string. A css_selector is ALWAYS routed to the selector parser (which itself handles a
    lone '#id', a lone bare root tag, and the compound '#id > tag:nth-of-type(n) > ...' form). A
    bare STRING with no selector punctuation is a convenience id lookup (a caller that already has
    an element id in hand)."""
    if isinstance(anchor, dict):
        kind = anchor.get("kind")
        value = anchor.get("value", "")
        if not isinstance(value, str) or not value:
            raise AnchorError(f"anchor has no string 'value': {anchor!r}")
        if kind == "element_id":
            return ("id", value)
        # css_selector, or an absent/unknown kind — treat the value as a selector string.
        return ("selector", value)
    if isinstance(anchor, str):
        if not anchor:
            raise AnchorError("empty anchor string")
        if anchor.startswith("#") or ">" in anchor or ":nth-of-type(" in anchor:
            return ("selector", anchor)
        return ("id", anchor)
    raise AnchorError(f"anchor must be a dict or string, got {type(anchor).__name__}")


def _parse_steps(value: str) -> tuple[str | None, str, list[tuple[str, int]]]:
    """Parse a selector into (root_id, root_tag, steps). Exactly one of root_id/root_tag is
    meaningful: a leading '#id' gives (id, '', steps); a leading bare 'tag' gives (None, tag,
    steps). `steps` is the list of (tag, nth) descendant steps after the root. A lone '#id' (no
    steps) is an id lookup; a lone bare 'tag' (no steps) is the document root."""
    parts = [p.strip() for p in value.split(">")]
    if any(not p for p in parts):
        raise AnchorError(f"malformed selector (empty step): {value!r}")
    head = parts[0]
    root_id: str | None = None
    root_tag = ""
    if head.startswith("#"):
        root_id = head[1:]
        if not _IDENT_RE.match(root_id):
            raise AnchorError(f"malformed ancestor-id root step {head!r} in {value!r}")
    else:
        if not _IDENT_RE.match(head):
            raise AnchorError(f"malformed root tag step {head!r} in {value!r}")
        root_tag = head
    steps: list[tuple[str, int]] = []
    for seg in parts[1:]:
        m = _STEP_RE.match(seg)
        if not m:
            raise AnchorError(
                f"unsupported selector step {seg!r} (only 'tag:nth-of-type(n)' is supported) in {value!r}"
                
            )
        steps.append((m.group(1), int(m.group(2))))
    return root_id, root_tag, steps


# ── resolution ────────────────────────────────────────────────────────────────────────────────

def _find_by_id(document: _El, elem_id: str) -> _El | None:
    stack = list(document.children)
    while stack:
        el = stack.pop()
        if el.attrs.get("id") == elem_id:
            return el
        stack.extend(reversed(el.children))
    return None


def _nth_child_of_type(parent: _El, tag: str, nth: int) -> _El | None:
    count = 0
    for c in parent.children:
        if c.tag == tag:
            count += 1
            if count == nth:
                return c
    return None


def _resolve_el(document: _El, anchor: Any) -> _El:
    kind, value = _normalize_anchor(anchor)
    if kind == "id":
        el = _find_by_id(document, value)
        if el is None:
            raise AnchorError(f"no element with id={value!r}")
        return el

    root_id, root_tag, steps = _parse_steps(value)
    if root_id is not None:
        cur = _find_by_id(document, root_id)
        if cur is None:
            raise AnchorError(f"ancestor id={root_id!r} not found (selector {value!r})")
    else:
        roots = _root_elements(document)
        if len(roots) == 1:
            cur = roots[0]
        else:
            cur = next((r for r in roots if r.tag == root_tag), None)
        if cur is None or cur.tag != root_tag:
            raise AnchorError(
                f"document-root step {root_tag!r} does not match the actual root (selector {value!r})"
                
            )
    for tag, nth in steps:
        nxt = _nth_child_of_type(cur, tag, nth)
        if nxt is None:
            raise AnchorError(
                f"no {tag}:nth-of-type({nth}) under {cur.tag} (selector {value!r})"
            )
        cur = nxt
    return cur


# ── public API ────────────────────────────────────────────────────────────────────────────────

def resolve(html: str, anchor: Any) -> Node:
    """Resolve `anchor` (dict or string, in infer's grammar) against `html`. Raises AnchorError if
    the anchor is unparseable or names no node."""
    return Node(_resolve_el(_build_tree(html), anchor))


def try_resolve(html: str, anchor: Any) -> Node | None:
    """resolve(), but returns None instead of raising when the anchor names no node. Still raises
    AnchorError for a genuinely UNPARSEABLE anchor (a bug, not an absence)."""
    document = _build_tree(html)
    kind, value = _normalize_anchor(anchor)  # may raise AnchorError for an unparseable anchor
    try:
        if kind == "id":
            el = _find_by_id(document, value)
            return Node(el) if el is not None else None
        return Node(_resolve_el(document, anchor))
    except AnchorError:
        return None


def exists(html: str, anchor: Any) -> bool:
    """True iff `anchor` names a node in `html`. Never raises for a well-formed-but-absent anchor
    (returns False); a frozen binding uses this and must not fail on a missing-node lookup being
    turned into a hard error elsewhere."""
    try:
        return try_resolve(html, anchor) is not None
    except AnchorError:
        return False


def document_path(html: str, anchor: Any) -> tuple[tuple[str, int], ...]:
    """The resolved node's stable structural identity (see Node.path)."""
    return resolve(html, anchor).path


def read_inner(html: str, anchor: Any) -> str:
    """The inner content (open-tag-end .. close-tag-start) of the anchored node. '' for a void
    element. Raises AnchorError if the anchor names no node."""
    return resolve(html, anchor).inner_text(html)


def replace_inner(html: str, anchor: Any, new_inner: str) -> str:
    """Return `html` with the anchored node's inner content replaced by `new_inner`. Raises
    AnchorError if the anchor names no node, or if it names a void element (no inner region)."""
    node = resolve(html, anchor)
    if node.is_void:
        raise AnchorError(
            f"anchor names a void element <{node.tag}> with no inner content region"
        )
    return html[: node.inner_start] + new_inner + html[node.inner_end:]


# ══════════════════════════════════════════════════════════════════════════════════════════════
# OFFICE / OOXML  —  the shared Word (.docx) anchor grammar + body-walk resolver
# ══════════════════════════════════════════════════════════════════════════════════════════════
#
# This module OWNS the Office anchor contract. It is the exact analogue of the HTML grammar at the
# top of this file, and is pinned normatively in core-architecture-spec.md §2 (the "Office anchor
# grammar" subsection). Every Office stage — the `infer-office` PRODUCER, `rebind-office`, and the
# Office fidelity harness — resolves EXACTLY this grammar via the functions below, so a run over
# `word/document.xml` cannot drift between producer and consumers (the failure that bit the HTML
# lane). The RSG carries these anchors under kind "ooxml_path" (the only Office kind the RSG schema
# admits — see rsg.schema.json $defs.anchor).
#
# GRAMMAR (a PEG restatement of what infer-office emits — see infer_office._anchor_for):
#     anchor      := {"kind": "ooxml_path", "value": path}     # (or the bare `path` string)
#     path        := body_path | bookmark_path
#     body_path   := "body" ("/" step)*        # rooted at the single w:body element (absolute)
#     bookmark_path := "bookmark(" NAME ")" ("/" step)*        # rooted at the element a named
#                                                              #   w:bookmarkStart opens on
#     step        := LOCAL "[" N "]"           # 1-based index among same-LOCAL-name ELEMENT
#                                              #   siblings, document order
#     LOCAL       := a namespace-stripped OOXML element local name (p, r, tbl, tr, tc, drawing, …)
#     N           := a positive 1-based integer
#     NAME        := a w:bookmarkStart/@w:name value (no '/' — bookmark names never contain one)
#
# THE ONE INDEXING RULE (single source of truth — `ooxml_local` + `ooxml_sibling_index`):
#   The index N counts among **same-local-name element siblings only**, 1-based, in document order,
#   counting ALL element children of the parent bucketed by local name. Non-content property
#   elements (w:pPr, w:rPr, w:sectPr, w:tblPr, w:tblGrid, w:trPr, w:tcPr, w:bookmarkStart/End, …)
#   therefore never perturb a run's or paragraph's index — each occupies its OWN local-name bucket.
#   Namespaces are stripped ("{uri}p" and "w:p" both -> "p"). This mirrors the HTML nth-of-type
#   rule (count among same-tag siblings) precisely. BOTH the etree-based producer (infer_office) and
#   the expat-based resolver (below) apply this identical rule; a cross-check test locks their
#   agreement in both directions.
#
# BOOKMARK SEMANTICS (single source of truth — `_ooxml_governed`):
#   A `bookmark(NAME)` root resolves to the element the matching w:bookmarkStart "opens on" — the
#   FIRST element sibling strictly AFTER that w:bookmarkStart within its parent (the run it wraps,
#   or the paragraph it precedes). This is the surgical-KPI archetype (a bookmark bracketing the
#   value run). A node governed by a named bookmark MUST anchor by the bookmark form; every other
#   node anchors by an absolute `body`-rooted path (the HTML "a node with an id anchors by
#   element_id; else by a selector rooted at its nearest id-bearing ancestor / the document root").
#
# Parsing stdlib: xml.parsers.expat (records byte spans so a byte/XML surgeon can splice
# word/document.xml without a DOM re-serialize) — no python-docx, no lxml. Spans are BYTE offsets
# into the document.xml bytes; text accessors decode utf-8.

_W_MAIN_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# Non-content OOXML property/marker elements: never emitted as RSG content nodes by the producer,
# but STILL counted in sibling indices (each in its own local-name bucket). Listed here for the
# resolver/consumers as documentation of the shared taxonomy — the resolver counts them implicitly.
OOXML_PROPERTY_LOCALS = frozenset(
    [
        "pPr", "rPr", "sectPr", "tblPr", "tblGrid", "gridCol", "trPr", "tcPr", "tblPrEx",
        "pStyle", "rStyle", "bookmarkStart", "bookmarkEnd", "proofErr", "lastRenderedPageBreak",
    ]
)

_OOXML_STEP_RE = re.compile(r"^([A-Za-z][\w.-]*)\[(\d+)\]$")
_OOXML_BOOKMARK_RE = re.compile(r"^bookmark\((?P<name>[^/]*)\)$")


def ooxml_local(qname: str) -> str:
    """Strip a namespace from an OOXML element/attribute name: '{uri}p' -> 'p', 'w:p' -> 'p',
    'p' -> 'p'. THE name-normalization half of the shared indexing rule."""
    if "}" in qname:
        return qname.rsplit("}", 1)[1]
    if ":" in qname:
        return qname.rsplit(":", 1)[1]
    return qname


def ooxml_sibling_index(child_qnames: list[str], position: int) -> int:
    """1-based index of the child at `position` among same-LOCAL-name siblings in `child_qnames`
    (already in document order). THE indexing half of the shared rule — called by BOTH the producer
    (over its etree children) and the resolver (over its expat children) so the two never drift."""
    target = ooxml_local(child_qnames[position])
    return 1 + sum(1 for i in range(position) if ooxml_local(child_qnames[i]) == target)


def ooxml_path_value(steps: list[tuple[str, int]]) -> str:
    """Build a body-rooted path string from steps: [] -> 'body'; [('p',3),('r',1)] ->
    'body/p[3]/r[1]'. (The production half of the shared grammar.)"""
    return "/".join(["body"] + [f"{local}[{n}]" for local, n in steps])


def ooxml_bookmark_value(name: str, steps: list[tuple[str, int]] | None = None) -> str:
    """Build a bookmark-rooted path string: 'bookmark(revenue_total)', optionally + '/step'*."""
    tail = [f"{local}[{n}]" for local, n in (steps or [])]
    return "/".join([f"bookmark({name})"] + tail)


def _parse_ooxml_steps(segment_str: str) -> list[tuple[str, int]]:
    steps: list[tuple[str, int]] = []
    for seg in segment_str.split("/"):
        seg = seg.strip()
        if not seg:
            raise AnchorError(f"malformed ooxml_path (empty step) in {segment_str!r}")
        m = _OOXML_STEP_RE.match(seg)
        if not m:
            raise AnchorError(
                f"unsupported ooxml_path step {seg!r} (only 'local[n]' is supported)"
            )
        steps.append((m.group(1), int(m.group(2))))
    return steps


def ooxml_parse_path(value: str) -> tuple[str | None, list[tuple[str, int]]]:
    """Parse an ooxml_path value into (bookmark_name_or_None, steps). A `body`-rooted path returns
    (None, steps); a `bookmark(NAME)`-rooted path returns (NAME, steps). (The parse half of the
    shared grammar — the inverse of ooxml_path_value / ooxml_bookmark_value.)"""
    value = value.strip()
    if not value:
        raise AnchorError("empty ooxml_path")
    head, sep, rest = value.partition("/")
    m = _OOXML_BOOKMARK_RE.match(head)
    if m is not None:
        name = m.group("name")
        if not name:
            raise AnchorError(f"empty bookmark name in {value!r}")
        return (name, _parse_ooxml_steps(rest) if rest else [])
    if head != "body":
        raise AnchorError(
            f"ooxml_path must start with 'body' or 'bookmark(NAME)', got {head!r}"
        )
    return (None, _parse_ooxml_steps(rest) if rest else [])


def _normalize_ooxml_anchor(anchor: Any) -> str:
    """Return the ooxml_path value string from an anchor dict ({'kind':'ooxml_path','value':…}) or a
    bare string. A non-ooxml_path kind is tolerated (the value is still parsed as a path) so a
    caller that hand-builds an anchor is not tripped by a kind typo."""
    if isinstance(anchor, dict):
        value = anchor.get("value", "")
        if not isinstance(value, str) or not value:
            raise AnchorError(f"ooxml anchor has no string 'value': {anchor!r}")
        return value
    if isinstance(anchor, str):
        if not anchor:
            raise AnchorError("empty ooxml anchor string")
        return anchor
    raise AnchorError(f"ooxml anchor must be a dict or string, got {type(anchor).__name__}")


# ── the OOXML element tree (expat; records source byte spans + document order + w:t text) ─────

class _OoxmlEl:
    __slots__ = (
        "tag", "attrs", "parent", "children", "text_parts",
        "open_start", "open_end", "close_start", "close_end", "self_closed",
    )

    def __init__(self, tag: str, attrs: dict[str, str], parent: _OoxmlEl | None) -> None:
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children: list[_OoxmlEl] = []
        self.text_parts: list[str] = []
        self.open_start = -1
        self.open_end = -1
        self.close_start = -1
        self.close_end = -1
        self.self_closed = False


def _end_of_start_tag(data: bytes, start: int) -> int:
    """Return the byte index just PAST the '>' that closes the start tag beginning at `data[start]`
    ('<'), respecting quoted attribute values (an attr value may legally contain a raw '>')."""
    i = start + 1
    n = len(data)
    quote = 0
    while i < n:
        ch = data[i]
        if quote:
            if ch == quote:
                quote = 0
        elif ch == 0x22 or ch == 0x27:  # " or '
            quote = ch
        elif ch == 0x3E:  # >
            return i + 1
        i += 1
    return n


class _OoxmlTreeBuilder:
    """Builds an ordered _OoxmlEl tree from document.xml BYTES using expat, recording each element's
    byte spans (open tag / inner / close tag) for byte-level surgery. Namespace processing is OFF so
    names arrive prefix-qualified (e.g. 'w:p'); `ooxml_local` strips the prefix."""

    def __init__(self, data: bytes) -> None:
        self._data = data
        self.root = _OoxmlEl("#document", {}, None)
        self._stack: list[_OoxmlEl] = [self.root]
        p = expat.ParserCreate()
        p.buffer_text = True
        p.StartElementHandler = self._start
        p.EndElementHandler = self._end
        p.CharacterDataHandler = self._chars
        # XXE / billion-laughs defense (stdlib-only floor — defusedxml is not on this plugin's
        # dependency path). A valid OOXML word/document.xml NEVER carries a DTD, so rejecting any
        # DOCTYPE closes both external-entity (XXE) and internal entity-expansion attacks at the
        # source (both require a DTD subset to declare entities), and we also refuse to fetch any
        # external entity. This treats a hostile template as DATA, never as instructions (§6).
        p.StartDoctypeDeclHandler = self._reject_dtd
        p.ExternalEntityRefHandler = self._reject_external_entity
        self._parser = p

    def _reject_dtd(self, *args: Any) -> None:
        raise AnchorError("DOCTYPE/DTD in document.xml is rejected (XXE / entity-expansion defense)")

    def _reject_external_entity(self, *args: Any) -> int:
        raise AnchorError("external entity reference in document.xml is rejected (XXE defense)")

    def _start(self, name: str, attrs: dict[str, str]) -> None:
        parent = self._stack[-1]
        el = _OoxmlEl(name, dict(attrs), parent)
        el.open_start = self._parser.CurrentByteIndex
        el.open_end = _end_of_start_tag(self._data, el.open_start)
        el.self_closed = el.open_end >= 2 and self._data[el.open_end - 2] == 0x2F  # '/>' -> self-close
        parent.children.append(el)
        self._stack.append(el)

    def _end(self, name: str) -> None:
        el = self._stack.pop()
        if el.self_closed:
            el.close_start = el.open_end
            el.close_end = el.open_end
        else:
            el.close_start = self._parser.CurrentByteIndex
            gt = self._data.find(b">", el.close_start)
            el.close_end = (gt + 1) if gt != -1 else len(self._data)

    def _chars(self, data: str) -> None:
        self._stack[-1].text_parts.append(data)

    def build(self) -> _OoxmlEl:
        self._parser.Parse(self._data, True)
        return self.root


def _ooxml_document_bytes(source: Any) -> bytes:
    """Normalize an OOXML source to the raw `word/document.xml` bytes. Accepts: the document.xml as
    str or bytes, OR a whole `.docx` as zip bytes (opened in-memory — never a filesystem path read,
    preserving this module's no-file-I/O contract; the caller does any disk read)."""
    if isinstance(source, str):
        source = source.encode("utf-8")
    if isinstance(source, (bytes, bytearray)):
        raw = bytes(source)
        if raw[:2] == b"PK":  # a zip (OPC package) — extract word/document.xml in-memory
            try:
                with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                    return zf.read("word/document.xml")
            except KeyError:
                raise AnchorError("zip has no word/document.xml part (not a Word .docx?)")
            except zipfile.BadZipFile as exc:
                raise AnchorError(f"source looks like a zip but is corrupt: {exc}")
        return raw
    raise AnchorError(f"ooxml source must be str, bytes, or .docx zip bytes, got {type(source).__name__}")


def _ooxml_build_tree(data: bytes) -> _OoxmlEl:
    return _OoxmlTreeBuilder(data).build()


def _ooxml_find_local(el: _OoxmlEl, local: str) -> _OoxmlEl | None:
    """Depth-first search for the first descendant (or `el` itself) with the given local name."""
    stack = list(el.children)
    while stack:
        cur = stack.pop(0)
        if ooxml_local(cur.tag) == local:
            return cur
        stack[:0] = cur.children
    return None


def _ooxml_nth_child(parent: _OoxmlEl, local: str, nth: int) -> _OoxmlEl | None:
    count = 0
    for c in parent.children:
        if ooxml_local(c.tag) == local:
            count += 1
            if count == nth:
                return c
    return None


def _ooxml_governed(tree: _OoxmlEl, name: str) -> _OoxmlEl | None:
    """The element a named w:bookmarkStart opens on: the first element sibling strictly after it
    within its parent (see BOOKMARK SEMANTICS above). None if the bookmark or a following sibling is
    absent."""
    stack: list[_OoxmlEl] = list(tree.children)
    while stack:
        cur = stack.pop(0)
        if ooxml_local(cur.tag) == "bookmarkStart":
            bm_name = None
            for k, v in cur.attrs.items():
                if ooxml_local(k) == "name":
                    bm_name = v
                    break
            if bm_name == name and cur.parent is not None:
                sibs = cur.parent.children
                idx = sibs.index(cur)
                for j in range(idx + 1, len(sibs)):
                    return sibs[j]
                return None
        stack[:0] = cur.children
    return None


def _ooxml_type_index(el: _OoxmlEl) -> int:
    """1-based index of `el` among its same-local-name siblings (the shared indexing rule, applied
    on the resolver side)."""
    if el.parent is None:
        return 1
    local = ooxml_local(el.tag)
    count = 0
    for c in el.parent.children:
        if ooxml_local(c.tag) == local:
            count += 1
            if c is el:
                return count
    return count


# ── the resolved OOXML node handed to every consumer ──────────────────────────────────────────

class OoxmlNode:
    """A resolved OOXML anchor target. Exposes the node's stable structural identity (`path` — for
    the harness) and the document.xml byte spans a surgeon needs (open tag / inner / outer — for
    byte/XML edits), plus the concatenated w:t text of the region."""

    __slots__ = ("_el", "_doc")

    def __init__(self, el: _OoxmlEl, doc: bytes) -> None:
        self._el = el
        self._doc = doc

    @property
    def local_name(self) -> str:
        return ooxml_local(self._el.tag)

    @property
    def tag(self) -> str:
        return self._el.tag

    @property
    def attrs(self) -> dict[str, str]:
        return dict(self._el.attrs)

    @property
    def is_empty(self) -> bool:
        """A self-closed element (<w:t/>), OR a paired element whose close tag was never seen."""
        return self._el.self_closed or self._el.close_start == -1

    @property
    def open_start(self) -> int:
        return self._el.open_start

    @property
    def open_end(self) -> int:
        return self._el.open_end

    @property
    def inner_start(self) -> int:
        return self._el.open_end

    @property
    def inner_end(self) -> int:
        return self._el.close_start if self._el.close_start != -1 else self._el.open_end

    @property
    def outer_start(self) -> int:
        return self._el.open_start

    @property
    def outer_end(self) -> int:
        return self._el.close_end if self._el.close_end != -1 else self._el.open_end

    @property
    def path(self) -> tuple[tuple[str, int], ...]:
        """The stable structural identity: the (local_name, index) steps from the w:body element
        down to this node (EXCLUDING body itself). Absolute — independent of whether the anchor was
        expressed as a body path or a bookmark path — so two anchors naming the same node share one
        `path`. () for the body element itself."""
        steps: list[tuple[str, int]] = []
        cur: _OoxmlEl | None = self._el
        while cur is not None and ooxml_local(cur.tag) != "body" and cur.tag != "#document":
            steps.append((ooxml_local(cur.tag), _ooxml_type_index(cur)))
            cur = cur.parent
        return tuple(reversed(steps))

    def open_tag_bytes(self) -> bytes:
        return self._doc[self._el.open_start:self._el.open_end]

    def inner_bytes(self) -> bytes:
        if self.is_empty:
            return b""
        return self._doc[self.inner_start:self.inner_end]

    def outer_bytes(self) -> bytes:
        return self._doc[self.outer_start:self.outer_end]

    def text(self) -> str:
        """The concatenated text of every descendant w:t (and this node, if it is a w:t). For a run
        this is its value; for a paragraph/cell it is the aggregate text of the region."""
        parts: list[str] = []
        stack = [self._el]
        while stack:
            cur = stack.pop(0)
            if ooxml_local(cur.tag) == "t":
                parts.append("".join(cur.text_parts))
            stack[:0] = cur.children
        return "".join(parts)

    def replace_inner_bytes(self, new_inner: bytes) -> bytes:
        """Return the FULL document.xml bytes with this node's inner region replaced by `new_inner`
        (a byte-level surgical edit). Raises AnchorError for a self-closed/empty element."""
        if self.is_empty:
            raise AnchorError(
                f"anchor names an empty element <{self.tag}> with no inner content region"
            )
        return self._doc[: self.inner_start] + new_inner + self._doc[self.inner_end:]


# ── OOXML public API (mirrors the HTML resolve/try_resolve/exists/document_path surface) ──────

def _ooxml_resolve_el(tree: _OoxmlEl, anchor: Any) -> _OoxmlEl:
    value = _normalize_ooxml_anchor(anchor)
    name, steps = ooxml_parse_path(value)
    if name is not None:
        cur = _ooxml_governed(tree, name)
        if cur is None:
            raise AnchorError(f"bookmark {name!r} not found (or it opens on nothing)")
    else:
        body = _ooxml_find_local(tree, "body")
        if body is None:
            raise AnchorError("document has no w:body")
        cur = body
    for local, nth in steps:
        nxt = _ooxml_nth_child(cur, local, nth)
        if nxt is None:
            raise AnchorError(
                f"no {local}[{nth}] under <{cur.tag}> (ooxml_path {value!r})"
            )
        cur = nxt
    return cur


def ooxml_resolve(source: Any, anchor: Any) -> OoxmlNode:
    """Resolve an Office `anchor` (dict {'kind':'ooxml_path','value':…} or a bare path string)
    against `source` (word/document.xml str/bytes, or `.docx` zip bytes). Raises AnchorError if the
    anchor is unparseable or names no node."""
    doc = _ooxml_document_bytes(source)
    tree = _ooxml_build_tree(doc)
    return OoxmlNode(_ooxml_resolve_el(tree, anchor), doc)


def ooxml_try_resolve(source: Any, anchor: Any) -> OoxmlNode | None:
    """ooxml_resolve(), but returns None instead of raising when the anchor names no node. Still
    raises AnchorError for a genuinely UNPARSEABLE anchor (a malformed grammar is a bug, not an
    absence) — the parse happens BEFORE the not-found catch, so a bad path surfaces loudly."""
    doc = _ooxml_document_bytes(source)
    tree = _ooxml_build_tree(doc)
    ooxml_parse_path(_normalize_ooxml_anchor(anchor))  # raises for a malformed/unparseable anchor
    try:
        return OoxmlNode(_ooxml_resolve_el(tree, anchor), doc)
    except AnchorError:
        return None


def ooxml_exists(source: Any, anchor: Any) -> bool:
    """True iff `anchor` names a node in `source`. Never raises for a well-formed-but-absent anchor."""
    try:
        return ooxml_try_resolve(source, anchor) is not None
    except AnchorError:
        return False


def ooxml_document_path(source: Any, anchor: Any) -> tuple[tuple[str, int], ...]:
    """The resolved node's stable structural identity (see OoxmlNode.path)."""
    return ooxml_resolve(source, anchor).path


def ooxml_read_inner(source: Any, anchor: Any) -> bytes:
    """The inner region bytes of the anchored node (b'' for an empty element)."""
    return ooxml_resolve(source, anchor).inner_bytes()


def ooxml_replace_inner(source: Any, anchor: Any, new_inner: bytes) -> bytes:
    """Return the FULL document.xml bytes with the anchored node's inner region replaced. Raises
    AnchorError if the anchor names no node or names an empty element."""
    return ooxml_resolve(source, anchor).replace_inner_bytes(new_inner)
