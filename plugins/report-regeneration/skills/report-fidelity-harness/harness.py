#!/usr/bin/env python3
"""
harness.py — report-regeneration fidelity harness (the 6-leg + period-coherence verifier).

The load-bearing wall of `report-regeneration`. Given a template report, a regenerated output,
the Binding Manifest that partitions it, and the new dataset, this runs every fidelity leg and
emits a `fidelity-receipt` (validates against ../../knowledge/fidelity-receipt.schema.json).

Legs (per core-architecture-spec.md §5):
    V1  value accuracy      — recompute expected value from new-data (2nd path) + locate at the
                              anchor + position-agnostic set-membership + cross-slot consistency.
                              proven, BLOCKING. (set-membership + cross-slot halves are ML-free.)
    V2  frozen-complement   — canonical node-diff of output vs template restricted to everything
                              OUTSIDE the surgical/regenerate anchors → must be empty. proven,
                              BLOCKING, fully ML-free.
    V3  re-inference iso    — rule-based coarse structural cross-check (section/table/image/heading
                              /row counts read straight from the container) + tag-skeleton
                              isomorphism. proven, BLOCKING. (coarse count half is ML-free.)
    V4  taint egress        — dictionary of the OLD report's distinct values + identity strings,
                              scanned over the DECODED delivered container (visible text + every
                              attribute value + script/style CDATA + base64/data-URI blobs), typed
                              value-space normalized. proven, BLOCKING, fully ML-free.
    V5  render referee      — the standalone Playwright module (render_referee.py) is wired in for
                              HTML (real render under the optional venv); LibreOffice `soffice`
                              render→image for Office. `not_captured` gracefully when the renderer is
                              absent — never a fake pass.
    V6  manifest coverage   — non-ML value-token scan of the OUTPUT; a value slot the manifest
                              calls surgical/regenerate that the output presents as frozen/unbound
                              while still carrying a dataset value = coverage failure; a value-shaped
                              token in a frozen region = advisory needs-review (hard rule). proven,
                              BLOCKING, fully ML-free.
    +   period-coherence    — every rendered period label + every value's provenance period (incl.
                              PBI screenshot/figure) must match the new reporting period. proven,
                              BLOCKING, fully ML-free.

Two output formats (core-architecture-spec.md §1, §2.1, §6). The harness FORMAT-DETECTS html vs
Office (docx) by extension/magic (`PK\x03\x04` zip => office) and runs the matching leg
implementations; `--report-format` overrides. The HTML lane is unchanged. The Office lane runs the
same seven legs over the OOXML OPC container: V2 frozen-complement over the docx parts + a masked
canonical node-diff of `word/document.xml`; V3 coarse count cross-check + tag-skeleton isomorphism;
V4 taint-egress over the DECODED container — unzip EVERY part and scan `word/document.xml`,
`word/embeddings/*.xlsx` (the embedded chart-data cache — the client's full old dataset),
`word/charts/*.xml`, `docProps/core.xml`+`app.xml` (Author/Company/Title/lastModifiedBy — a direct
identity leak), `word/comments.xml`, and unaccepted `w:ins`/`w:del`; V6 value-coverage; and
period-coherence — all keyed on the shared OOXML anchor grammar in scripts/rr_anchor.py. The
metadata/comment/tracked-change purge is surfaced as a pre-emit expectation in manual_residue.

Receipt discipline (W5, verbatim): PROBE_ERROR != pass (a parse/harness crash never reads as
"fidelity OK"); any not_captured => overall PARTIAL, never PASS; overall PASS only when every leg
verdict is pass. TTL'd + environment-fingerprinted.

Usage:
    python3 harness.py --template t.html --output o.html --manifest m.json --new-data d.json \
        --format json [--report-format html|office] [--taint taint.json] [--disable-leg V4 ...] [--ttl 3600]
    python3 harness.py --template t.docx --output o.docx --manifest m.json --new-data d.json  # office (auto-detected)

Constraints (binding): stdlib-only (zipfile/xml.etree/base64), runs on Python 3.9.6. No pip
installs, no network beyond the optional local render. V2, V4, V6, and period-coherence are
genuinely ML-free, for BOTH formats. Reads only; the only write is the receipt to stdout.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html.parser
import importlib.util
import io
import json
import os
import platform
import re
import sys
import uuid
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path

# The SHARED anchor resolver (../../scripts/rr_anchor.py). V2/V3 mask the manifest's
# surgical/regenerate/needs-review regions; when infer anchors an id-less node with a compound
# css_selector (e.g. "#tbl-region-revenue > tfoot:nth-of-type(1) > tr:nth-of-type(1) > td:...")
# this resolver maps it to a stable structural PATH that harness's own tree can match — so the
# verifier excludes exactly the regions rebind was licensed to touch, whatever anchor shape infer
# used. Without it, a compound-anchored bound region reads as a frozen-complement violation.
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import rr_anchor  # noqa: E402

RECEIPT_VERSION = "1.0.0"
DEFAULT_TTL_SECONDS = 3600

# Elements that never carry a closing tag (HTML void elements). html.parser fires handle_starttag
# for these with no matching handle_endtag, so the tree builder must not push them on the stack.
VOID_ELEMENTS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
})

# Non-rendering subtrees excluded from the RENDERED-value scans (V6 / period-coherence). V4 scans
# these on purpose (they are a hidden-channel leak surface); the rendered-value legs must not.
NON_RENDERED_TAGS = frozenset({"script", "style", "head", "title"})

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}
_MONTH_ALT = "|".join(_MONTHS)

_RE_CURRENCY = re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?")
_RE_PERCENT = re.compile(r"[+-]?\d+(?:\.\d+)?%")
_RE_DATE_WORDS = re.compile(r"\b(?:" + _MONTH_ALT + r")\s+\d{1,2},\s*\d{4}", re.IGNORECASE)
_RE_DATE_ISO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
_RE_PERIOD_QY = re.compile(r"\bQ([1-4])\s+(\d{4})\b")
_RE_PERIOD_YQ = re.compile(r"\b(\d{4})-Q([1-4])\b")
_RE_GROUPED_NUM = re.compile(r"\b\d{1,3}(?:,\d{3})+\b")


class HarnessError(Exception):
    """Raised for path-guard / usage failures (surfaced as exit 2, never a fake pass)."""


# ─────────────────────────────────────────────────────────────────────────────
# Path guard — read-only verifier. Resolves symlinks, requires a real regular file,
# rejects NUL bytes and non-files (device nodes / fifos / directories). No network.
# ─────────────────────────────────────────────────────────────────────────────

def safe_read_path(raw: str) -> Path:
    if not raw or "\x00" in raw:
        raise HarnessError("empty or NUL-bearing path")
    try:
        resolved = Path(raw).resolve()
    except (OSError, RuntimeError) as exc:
        raise HarnessError(f"cannot resolve path {raw!r}: {exc}") from exc
    if not resolved.exists():
        raise HarnessError(f"input file not found: {raw!r} (resolved {resolved})")
    if not resolved.is_file():
        raise HarnessError(f"not a regular file: {raw!r} (resolved {resolved})")
    return resolved


def read_text(raw: str) -> str:
    return safe_read_path(raw).read_text(encoding="utf-8")


def load_json(raw: str) -> object:
    return json.loads(read_text(raw))


# ─────────────────────────────────────────────────────────────────────────────
# Lightweight HTML tree (shared by V2, V3, V4, V6, period-coherence). Zero ML.
# ─────────────────────────────────────────────────────────────────────────────

class Text:
    __slots__ = ("data",)

    def __init__(self, data: str) -> None:
        self.data = data


class Comment:
    __slots__ = ("data",)

    def __init__(self, data: str) -> None:
        self.data = data


class Decl:
    __slots__ = ("data",)

    def __init__(self, data: str) -> None:
        self.data = data


class Element:
    __slots__ = ("tag", "attrs", "attr", "children", "parent")

    def __init__(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tag = tag
        self.attrs = attrs
        self.attr = {k: (v if v is not None else "") for k, v in attrs}
        self.children: list[object] = []
        self.parent: Element | None = None

    @property
    def id(self) -> str | None:
        return self.attr.get("id")


class _TreeBuilder(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Element("#document", [])
        self.stack: list[Element] = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        el = Element(tag, attrs)
        el.parent = self.stack[-1]
        self.stack[-1].children.append(el)
        if tag not in VOID_ELEMENTS:
            self.stack.append(el)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        el = Element(tag, attrs)
        el.parent = self.stack[-1]
        self.stack[-1].children.append(el)

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return
        # No matching open tag — tolerate (lenient HTML), do not crash.

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(Text(data))

    def handle_comment(self, data: str) -> None:
        self.stack[-1].children.append(Comment(data))

    def handle_decl(self, data: str) -> None:
        self.stack[-1].children.append(Decl(data))


def parse_html(text: str) -> Element:
    builder = _TreeBuilder()
    builder.feed(text)
    builder.close()
    return builder.root


def iter_elements(node: Element):
    for child in node.children:
        if isinstance(child, Element):
            yield child
            yield from iter_elements(child)


def find_by_id(root: Element, elem_id: str) -> Element | None:
    for el in iter_elements(root):
        if el.id == elem_id:
            return el
    return None


def text_content(node: object, skip: frozenset = frozenset()) -> str:
    out: list[str] = []

    def rec(n: object) -> None:
        if isinstance(n, Text):
            out.append(n.data)
        elif isinstance(n, Element):
            if n.tag in skip:
                return
            for c in n.children:
                rec(c)

    rec(node)
    return "".join(out)


def typed_values_in(node: object, skip: frozenset = NON_RENDERED_TAGS) -> set[tuple[str, str]]:
    """Union the typed value tokens found in EACH text node separately. Per-node extraction is
    load-bearing: adjacent inline cells (e.g. <td>$1,203,400</td><td>25.0%</td>) concatenate to
    one string, and a merged '$1,203,40025.0%' would corrupt the value regex. A single value
    literal never spans a text-node boundary, so per-node extraction is both correct and safe."""
    vals: set[tuple[str, str]] = set()

    def rec(n: object) -> None:
        if isinstance(n, Text):
            vals.update(extract_typed_values(n.data))
        elif isinstance(n, Element):
            if n.tag in skip:
                return
            for c in n.children:
                rec(c)

    rec(node)
    return vals


# ─────────────────────────────────────────────────────────────────────────────
# Typed value-space normalization (V1 / V4 / V6 / period). Non-inference.
# ─────────────────────────────────────────────────────────────────────────────

def normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def canon_number(raw: str) -> str | None:
    cleaned = raw.replace(",", "").replace("$", "").replace("%", "").replace("+", "").strip()
    if not cleaned:
        return None
    try:
        f = float(cleaned)
    except ValueError:
        return None
    if f == int(f):
        return str(int(f))
    return repr(f)


def canon_date(raw: str) -> str | None:
    low = raw.lower()
    m = re.search(r"\b(" + _MONTH_ALT + r")\s+(\d{1,2}),\s*(\d{4})", low)
    if m:
        return f"{int(m.group(3)):04d}-{_MONTHS[m.group(1)]:02d}-{int(m.group(2)):02d}"
    m2 = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", raw)
    if m2:
        return f"{int(m2.group(1)):04d}-{int(m2.group(2)):02d}-{int(m2.group(3)):02d}"
    return None


def find_periods(text: str) -> set[str]:
    out: set[str] = set()
    for m in _RE_PERIOD_QY.finditer(text):
        out.add(f"{m.group(2)}-Q{m.group(1)}")
    for m in _RE_PERIOD_YQ.finditer(text):
        out.add(f"{m.group(1)}-Q{m.group(2)}")
    return out


def normalize_value(value: str, vtype: str) -> str | None:
    if vtype in ("currency", "percent", "number"):
        return canon_number(value)
    if vtype == "date":
        return canon_date(value)
    if vtype == "period":
        periods = find_periods(value)
        return sorted(periods)[0] if periods else None
    return normalize_ws(value)


def extract_typed_values(text: str) -> set[tuple[str, str]]:
    """Non-ML typed-token extractor. Returns a set of (type, canonical-value)."""
    vals: set[tuple[str, str]] = set()
    for m in _RE_CURRENCY.finditer(text):
        c = canon_number(m.group())
        if c is not None:
            vals.add(("currency", c))
    for m in _RE_PERCENT.finditer(text):
        c = canon_number(m.group())
        if c is not None:
            vals.add(("percent", c))
    for m in _RE_DATE_WORDS.finditer(text):
        d = canon_date(m.group())
        if d is not None:
            vals.add(("date", d))
    for m in _RE_DATE_ISO.finditer(text):
        d = canon_date(m.group())
        if d is not None:
            vals.add(("date", d))
    for p in find_periods(text):
        vals.add(("period", p))
    for m in _RE_GROUPED_NUM.finditer(text):
        c = canon_number(m.group())
        if c is not None:
            vals.add(("number", c))
    return vals


# ─────────────────────────────────────────────────────────────────────────────
# Manifest helpers
# ─────────────────────────────────────────────────────────────────────────────

_SIMPLE_ID_SELECTOR = re.compile(r"^#([A-Za-z][\w-]*)$")

# Classes whose anchored region V2/V3 permit to differ: surgical/regenerate (rebound value/asset)
# AND needs-review (rebind adds a visible flag badge + a data-rebind-flag attr to the node — a
# licensed annotation, not a frozen-complement violation). All three are "bound anchors" the
# manifest addresses; V2 asks "did anything change OUTSIDE the bound anchors?".
_MUTABLE_CLASSES = ("surgical", "regenerate", "needs-review")


def excluded_regions(manifest: dict, template_text: str) -> tuple:
    """The bound regions V2/V3 mask, resolved across BOTH anchor shapes infer emits:
      - element_id / simple '#id'  -> an element-id string (matched by Element.id)
      - compound css_selector      -> a stable structural PATH (tag, nth-of-type) tuple, resolved
                                      via the shared rr_anchor against the template.
    Returns (excluded_ids, excluded_paths)."""
    ids: set[str] = set()
    paths: set = set()
    for b in manifest.get("bindings", []):
        if b.get("class") not in _MUTABLE_CLASSES:
            continue
        anchor = b.get("anchor", {})
        kind = anchor.get("kind")
        value = anchor.get("value", "")
        if kind == "element_id":
            ids.add(value)
        elif kind == "css_selector":
            m = _SIMPLE_ID_SELECTOR.match(value or "")
            if m:
                ids.add(m.group(1))
            elif value:
                try:
                    paths.add(rr_anchor.document_path(template_text, anchor))
                except rr_anchor.AnchorError:
                    # An anchor that no longer resolves in the template is not maskable; V2 will
                    # then legitimately surface any change there rather than silently hide it.
                    pass
    return ids, paths


def _element_path(el: Element) -> tuple:
    """The (tag, nth-of-type)-from-document-root identity of `el`, computed with the SAME
    semantics rr_anchor uses (count among same-tag Element siblings, 1-based, document order), so
    a path resolved by rr_anchor over the source string matches the node in harness's tree."""
    steps: list = []
    cur = el
    while cur is not None and cur.tag != "#document":
        parent = cur.parent
        if parent is None:
            nth = 1
        else:
            same = [c for c in parent.children if isinstance(c, Element) and c.tag == cur.tag]
            nth = same.index(cur) + 1
        steps.append((cur.tag, nth))
        cur = parent
    return tuple(reversed(steps))


def excluded_objects(root: Element, excluded_ids: set, excluded_paths: set) -> set:
    """Resolve (excluded_ids, excluded_paths) against `root` into a set of id(element) object
    identities — the elements whose subtree V2/V3 mask."""
    objs: set = set()
    for el in iter_elements(root):
        if el.id is not None and el.id in excluded_ids:
            objs.add(id(el))
        elif excluded_paths and _element_path(el) in excluded_paths:
            objs.add(id(el))
    return objs


def value_domain(new_data: dict) -> set[tuple[str, str]]:
    domain: set[tuple[str, str]] = set()
    for spec in new_data.get("values", {}).values():
        n = normalize_value(spec["value"], spec["type"])
        if n is not None:
            domain.add((spec["type"], n))
            domain.add(("number", n) if spec["type"] == "currency" else (spec["type"], n))
    return domain


# ─────────────────────────────────────────────────────────────────────────────
# Leg V1 — value accuracy (recompute 2nd path + anchor + set-membership + cross-slot)
# ─────────────────────────────────────────────────────────────────────────────

def leg_v1(template_root: Element, output_root: Element, manifest: dict, new_data: dict) -> dict:
    values = new_data.get("values", {})
    output_typed = typed_values_in(output_root)

    # expression -> bindings that carry it (surgical value slots addressed by element_id)
    expr_bindings: dict[str, list[dict]] = {}
    for b in manifest.get("bindings", []):
        dq = b.get("data_query")
        if dq and dq.get("expression") and b.get("anchor", {}).get("kind") == "element_id":
            expr_bindings.setdefault(dq["expression"], []).append(b)

    anchor_failures: list[str] = []
    membership_failures: list[str] = []
    crossslot_failures: list[str] = []

    # (b) position-agnostic set-membership — ML-free half, over every new-source value.
    for key, spec in values.items():
        expected = normalize_value(spec["value"], spec["type"])
        if expected is None:
            continue
        if (spec["type"], expected) not in output_typed:
            membership_failures.append(
                "{}={!r} recomputed from new source appears nowhere in output".format(key, spec["value"])
            )

    # (a) locate-at-anchor + cross-slot — P3 #14: BOTH the binding index (expr_bindings) and the
    # value lookup key on the SAME identity, the binding's data_query.expression. Iterating the
    # bindings and resolving each expression's expected value from `values[expr]` makes it
    # impossible for a values-key vs expression mismatch to silently no-op the anchor half down to
    # set-membership-only (the prior code keyed the index by expression but looked it up by the
    # values-dict key, which coincide only by convention).
    for expr, bindings_for_expr in expr_bindings.items():
        spec = values.get(expr)
        if spec is None:
            continue
        vtype = spec["type"]
        expected = normalize_value(spec["value"], vtype)
        if expected is None:
            continue
        expected_token = (vtype, expected)

        slot_values: list[str] = []
        for b in bindings_for_expr:
            node = find_by_id(output_root, b["anchor"]["value"])
            if node is None:
                anchor_failures.append(
                    "anchor #{} for {} missing from output".format(b["anchor"]["value"], expr)
                )
                continue
            node_typed = typed_values_in(node)
            typed_of_kind = sorted(v for (t, v) in node_typed if t == vtype)
            if expected_token not in node_typed:
                anchor_failures.append(
                    "#{} carries {} not {!r} (expected {})".format(
                        b["anchor"]["value"], typed_of_kind or "no value", spec["value"], expected
                    )
                )
            if typed_of_kind:
                slot_values.append(typed_of_kind[0])

        # cross-slot consistency — every slot bound to the same expression must agree (ML-free).
        distinct = sorted(set(slot_values))
        if len(distinct) > 1:
            crossslot_failures.append(
                f"{expr} bound to {len(slot_values)} slots that disagree: {distinct}"
            )

    fired = anchor_failures or membership_failures or crossslot_failures
    verdict = "fail" if fired else "pass"
    evidence_parts = []
    if anchor_failures:
        evidence_parts.append("anchor: " + "; ".join(anchor_failures))
    if membership_failures:
        evidence_parts.append("set-membership(ML-free): " + "; ".join(membership_failures))
    if crossslot_failures:
        evidence_parts.append("cross-slot(ML-free): " + "; ".join(crossslot_failures))
    if not evidence_parts:
        evidence_parts.append(
            f"all {len(values)} recomputed values landed at their anchors and appear in-document; "
            "no cross-slot disagreement"
        )
    return {
        "leg": "V1",
        "verdict": verdict,
        "label": "proven",
        "inference_independent": False,  # recompute path is inference-adjacent; set-membership/cross-slot halves are ML-free
        "blocking": True,
        "evidence": " | ".join(evidence_parts),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Leg V2 — frozen-complement diff (canonical node-diff outside surgical/regen anchors)
# ─────────────────────────────────────────────────────────────────────────────

def canonical_tokens(node: object, excluded_objs: set) -> list[str]:
    toks: list[str] = []

    def rec(n: object) -> None:
        if isinstance(n, Text):
            t = normalize_ws(n.data)
            if t:
                toks.append("#text:" + t)
        elif isinstance(n, Comment):
            # Comments are purged as a hard pre-emit step (spec §6.6), so a comment-free real
            # output vs a comment-bearing template is EXPECTED, not a fidelity violation. Excluding
            # them keeps V2 from false-positiving on every real regeneration. (An injected
            # instruction comment is the partition-anomaly gate's job, not V2's.)
            return
        elif isinstance(n, Decl):
            toks.append("#decl:" + normalize_ws(n.data))
        elif isinstance(n, Element):
            if id(n) in excluded_objs:
                # a bound (surgical/regenerate/needs-review) anchor: value + attrs + inner are all
                # legitimately mutable, so mask the whole subtree to a single identity placeholder
                # (position preserved; the same placeholder in template + output => they match).
                toks.append(f"[ANCHOR:{n.tag}#{n.id or ''}]")
                return
            attrs = " ".join(
                "{}={!r}".format(k, v if v is not None else "")
                for k, v in sorted(n.attrs, key=lambda kv: kv[0])
            )
            toks.append(f"<{n.tag} {attrs}>")
            for c in n.children:
                rec(c)
            toks.append(f"</{n.tag}>")

    rec(node)
    return toks


def leg_v2(template_root: Element, output_root: Element, manifest: dict, template_text: str) -> dict:
    ids, paths = excluded_regions(manifest, template_text)
    tmpl = canonical_tokens(template_root, excluded_objects(template_root, ids, paths))
    out = canonical_tokens(output_root, excluded_objects(output_root, ids, paths))
    if tmpl == out:
        return {
            "leg": "V2", "verdict": "pass", "label": "proven",
            "inference_independent": True, "blocking": True,
            "evidence": f"frozen complement byte/canonically identical outside {len(ids) + len(paths)} bound "
                        f"anchors ({len(tmpl)} canonical tokens matched)",
        }
    # first divergence
    n = min(len(tmpl), len(out))
    idx = n
    for i in range(n):
        if tmpl[i] != out[i]:
            idx = i
            break
    t_tok = tmpl[idx] if idx < len(tmpl) else "(end)"
    o_tok = out[idx] if idx < len(out) else "(end)"
    return {
        "leg": "V2", "verdict": "fail", "label": "proven",
        "inference_independent": True, "blocking": True,
        "evidence": f"chrome changed outside bound anchors at token {idx}: template {t_tok[:120]!r} != output "
                    f"{o_tok[:120]!r}",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Leg V3 — re-inference isomorphism (ML-free coarse count cross-check + tag skeleton)
# ─────────────────────────────────────────────────────────────────────────────

def coarse_counts(root: Element) -> dict[str, int]:
    counts = {"section": 0, "table": 0, "img": 0, "heading": 0, "tr": 0}
    for el in iter_elements(root):
        if el.tag == "section":
            counts["section"] += 1
        elif el.tag == "table":
            counts["table"] += 1
        elif el.tag == "img":
            counts["img"] += 1
        elif el.tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            counts["heading"] += 1
        elif el.tag == "tr":
            counts["tr"] += 1
    return counts


def tag_skeleton(root: Element, excluded_objs: set = frozenset()) -> list[str]:
    """The pre-order tag sequence. A bound (surgical/regenerate/needs-review) anchor's tag is kept
    (position preserved) but its SUBTREE is masked — a regenerated narrative may carry a different
    inner tag structure, and rebind injects a needs-review badge <span>, both legitimately inside a
    bound region. The coarse counts (leg_v3, ML-free) stay UNMASKED as the primary structural
    signal; only this fine skeleton masks the mutable regions."""
    out: list[str] = []

    def rec(el: Element) -> None:
        for child in el.children:
            if isinstance(child, Element):
                out.append(child.tag)
                if id(child) not in excluded_objs:
                    rec(child)

    rec(root)
    return out


def leg_v3(template_root: Element, output_root: Element, manifest: dict, template_text: str) -> dict:
    tc = coarse_counts(template_root)
    oc = coarse_counts(output_root)
    diffs = [f"{k}: template={tc[k]} output={oc[k]}" for k in tc if tc[k] != oc[k]]
    ids, paths = excluded_regions(manifest, template_text)
    skeleton_equal = (
        tag_skeleton(template_root, excluded_objects(template_root, ids, paths))
        == tag_skeleton(output_root, excluded_objects(output_root, ids, paths))
    )
    if diffs:
        return {
            "leg": "V3", "verdict": "fail", "label": "proven",
            "inference_independent": False,  # coarse-count half ML-free; fine isomorphism is inference-adjacent (stated)
            "blocking": True,
            "evidence": "rule-based coarse structural cross-check (ML-free) fired — count mismatch: "
                        + "; ".join(diffs),
        }
    if not skeleton_equal:
        return {
            "leg": "V3", "verdict": "fail", "label": "proven",
            "inference_independent": False, "blocking": True,
            "evidence": "coarse counts match but tag-skeleton isomorphism failed (structure reordered)",
        }
    return {
        "leg": "V3", "verdict": "pass", "label": "proven",
        "inference_independent": False, "blocking": True,
        "evidence": f"coarse counts (ML-free) match {tc}; tag-skeleton isomorphic",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Leg V4 — taint-dictionary egress over the DECODED delivered container
# ─────────────────────────────────────────────────────────────────────────────

def derive_taint(template_text: str, override: dict | None) -> dict[str, str]:
    if override:
        return dict(override)
    # Default: read the labeled TAINT DICTIONARY block the template documents in its own comment
    # (the old-artifact literals). This is DERIVE-from-comment; the tree-walk SCAN excludes
    # comments, so a documentation comment in the TEMPLATE never self-triggers V4 — but the V4
    # raw-byte backstop scans the OUTPUT's full bytes (comments included), and a legitimate output
    # has had those comments stripped by rebind (spec §6.6), so a surviving old-client comment in
    # the OUTPUT is a genuine leak the backstop catches.
    out: dict[str, str] = {}
    for m in re.finditer(r'(old_\w+):\s*"([^"]+)"', template_text):
        out[m.group(1)] = m.group(2)
    return out


def _ingest_base64_run(v: str, text_parts: list, typed: set) -> None:
    """Decode a base64/data-URI run so an embedded blob's literals are scanned. On an UNDECODABLE
    blob the raw base64 bytes are still appended (P3 #12: a malformed blob is never swallowed
    unscanned — a taint literal spliced into a corrupt data-URI must still be caught)."""
    b64 = v.split("base64,", 1)[1].strip()
    try:
        decoded = base64.b64decode(b64, validate=False)
        blob = decoded.decode("utf-8", "replace")
        text_parts.append(blob)
        text_parts.append(decoded.decode("latin-1", "replace"))
        typed.update(extract_typed_values(blob))
    except Exception:  # malformed blob: scan the raw base64 literal rather than drop it
        text_parts.append(b64)
        typed.update(extract_typed_values(b64))


def _decoded_container(root: Element) -> tuple[str, set[tuple[str, str]]]:
    """The delivered/decoded container V4 scans: all text (incl. script/style CDATA — a hidden
    leak channel), every attribute value, and base64/data-URI blobs decoded (P0 #11: base64 is
    now decoded from Text-node CDATA too, not only attributes). HTML comments and the DOCTYPE are
    EXCLUDED here by construction (they are not Text nodes); the surviving-comment leak channel is
    covered by leg_v4's raw-byte backstop over the full delivered bytes."""
    text_parts: list[str] = []
    typed: set[tuple[str, str]] = set()

    def rec(n: object) -> None:
        if isinstance(n, Text):  # comments/decl are not Text nodes => excluded here (see backstop)
            text_parts.append(n.data)
            typed.update(extract_typed_values(n.data))
            if "base64," in n.data:
                _ingest_base64_run(n.data, text_parts, typed)
        elif isinstance(n, Element):
            for _, v in n.attrs:
                if v:
                    text_parts.append(v)
                    typed.update(extract_typed_values(v))
                    if "base64," in v:
                        _ingest_base64_run(v, text_parts, typed)
            for c in n.children:
                rec(c)

    rec(root)
    corpus = " ".join(text_parts)
    return corpus, typed


_UNIT_MULT = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000, "bn": 1_000_000_000}
_RE_UNIT_MAG = re.compile(r"[$€£¥+\-]?\s?(\d+(?:\.\d+)?)\s?(k|m|b|bn)", re.IGNORECASE)
_RE_CURRENCY_FULL = re.compile(r"[$€£¥]\s?\d[\d,]*(?:\.\d+)?")
_RE_PERCENT_FULL = re.compile(r"[+-]?\d+(?:\.\d+)?\s?%")
_RE_PERIOD_FULL = re.compile(r"Q[1-4]\s+\d{4}|\d{4}-Q[1-4]", re.IGNORECASE)
_RE_DATE_FULL = re.compile(r"(?:" + _MONTH_ALT + r")\s+\d{1,2},\s*\d{4}|\d{4}-\d{2}-\d{2}", re.IGNORECASE)
_RE_NUMBER_FULL = re.compile(r"[+-]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|[+-]?\d+(?:\.\d+)?")


def taint_shape(raw: str) -> tuple[str, str]:
    """Type a taint LITERAL from its OWN shape (P3 #15) — never from a key-name heuristic (a
    `old_gross_bookings` key carrying `$3,102,450` is still a currency; a `old_title` carrying an
    identity string that merely CONTAINS a quarter token stays an identity). Returns (kind, canon)
    with kind in {currency, percent, number, date, period, identity}. A unit-abbrev magnitude
    (`$3.1M` / `500K` / `2.4bn`) is normalized to its full canonical number so a taint written with
    a magnitude suffix still matches the expanded figure in the corpus. A literal is typed only when
    it is ENTIRELY that shape (full-match) — otherwise it is an identity string."""
    s = raw.strip()
    mag = _RE_UNIT_MAG.fullmatch(s)
    if mag:
        val = float(mag.group(1)) * _UNIT_MULT[mag.group(2).lower()]
        c = str(int(val)) if val == int(val) else repr(val)
        return ("currency" if s[:1] in "$€£¥" else "number", c)
    if _RE_CURRENCY_FULL.fullmatch(s):
        c = canon_number(s)
        if c is not None:
            return ("currency", c)
    if _RE_PERCENT_FULL.fullmatch(s):
        c = canon_number(s)
        if c is not None:
            return ("percent", c)
    if _RE_PERIOD_FULL.fullmatch(s):
        periods = find_periods(s)
        if periods:
            return ("period", sorted(periods)[0])
    if _RE_DATE_FULL.fullmatch(s):
        d = canon_date(s)
        if d is not None:
            return ("date", d)
    if _RE_NUMBER_FULL.fullmatch(s):
        c = canon_number(s)
        if c is not None:
            return ("number", c)
    return ("identity", normalize_ws(s).lower())


def _scan_taint(corpus_norm: str, corpus_typed: set, taint: dict[str, str],
                corpus_numbers: set | None = None) -> list[str]:
    """The shared, ML-free taint match — used by both the HTML and Office V4 legs. Each taint
    literal is typed from its OWN shape (see taint_shape): a value literal matches against the typed
    value-space (so a reformat/round/locale survival still hits), an identity string matches as a
    normalized substring. `corpus_numbers` (Office) is the set of canonical BARE numeric tokens in
    the decoded container — an embedded-xlsx data cache stores raw unformatted figures (e.g.
    `1284500`, no `$`/commas), so a value-taint match also consults the raw-number set the typed
    extractor never sees."""
    hits: list[str] = []
    for key, raw in taint.items():
        if not raw:
            continue
        kind, c = taint_shape(raw)
        if kind in ("currency", "number"):
            if c is not None and (
                ("currency", c) in corpus_typed or ("number", c) in corpus_typed
                or (corpus_numbers is not None and c in corpus_numbers)
            ):
                hits.append(f"{key}={raw!r} (typed {kind} / raw-cache match)")
        elif kind == "percent":
            if c is not None and (
                ("percent", c) in corpus_typed
                or (corpus_numbers is not None and c in corpus_numbers)
            ):
                hits.append(f"{key}={raw!r} (typed percent / raw-cache match)")
        elif kind in ("date", "period"):
            if (kind, c) in corpus_typed:
                hits.append(f"{key}={raw!r} (typed {kind} match)")
        else:  # identity string (company/author/source-filename/title/lastModifiedBy)
            if c and c in corpus_norm:
                hits.append(f"{key}={raw!r} (identity-string match)")
    return hits


def _v4_leg(corpus: str, corpus_typed: set, taint: dict[str, str], surface: str,
            corpus_numbers: set | None = None) -> dict:
    """Assemble the V4 legReceipt from a decoded-container corpus. `surface` names the scan surface
    (for evidence). Shared by leg_v4 (HTML) and leg_v4_office (OOXML)."""
    # P1 #2 — a V4 PASS is only meaningful against a NON-EMPTY taint dictionary. An empty derived
    # taint set with no --taint override cannot prove "no old-client leak survives" (there is
    # nothing to look for), so V4 degrades to not_captured => overall PARTIAL, never a vacuous PASS.
    if not any(v for v in taint.values()):
        return {
            "leg": "V4", "verdict": "not_captured", "label": "proven",
            "inference_independent": True, "blocking": True,
            "evidence": "no non-empty taint source (no --taint override and none derivable from the "
                        "template's old-artifact literals) — V4 cannot prove no old-client leak over "
                        + surface + "; not_captured (never a vacuous pass).",
        }
    hits = _scan_taint(normalize_ws(corpus).lower(), corpus_typed, taint, corpus_numbers)
    if hits:
        return {
            "leg": "V4", "verdict": "fail", "label": "proven",
            "inference_independent": True, "blocking": True,
            "evidence": "old-client taint survived into " + surface + ": " + "; ".join(hits),
        }
    return {
        "leg": "V4", "verdict": "pass", "label": "proven",
        "inference_independent": True, "blocking": True,
        "evidence": f"no member of the {len(taint)}-entry taint dictionary survives into " + surface,
    }


def leg_v4(output_root: Element, taint: dict[str, str], output_text: str | None = None) -> dict:
    corpus, corpus_typed = _decoded_container(output_root)
    surface = "the decoded container (visible text + attrs + script/style + base64 blobs)"
    if output_text is not None:
        # P0 #1(b) — RAW-BYTE BACKSTOP: the tree-walk decoded container excludes HTML comments and
        # the DOCTYPE (they are not Text nodes), which is exactly where an old-client TAINT comment
        # block would survive if rebind's pre-emit comment purge were bypassed. Scan the FULL
        # delivered bytes (comments/decls included) so any surviving old-client comment with a taint
        # hit forces V4 FAIL. A legitimate output has had those comments stripped by rebind, so this
        # never false-triggers on a real regeneration.
        corpus = corpus + " " + output_text
        corpus_typed = corpus_typed | extract_typed_values(output_text)
        surface += " + the full delivered bytes (comments/DOCTYPE — raw-byte backstop)"
    return _v4_leg(corpus, corpus_typed, taint, surface)


# ─────────────────────────────────────────────────────────────────────────────
# Leg V5 — render referee. HTML wires in the standalone render_referee.py (real Playwright render
# under the optional venv); Office renders via LibreOffice `soffice`. not_captured (never a fake
# pass) when the renderer is absent (the stdlib default).
# ─────────────────────────────────────────────────────────────────────────────

def _import_render_referee():
    """Load the sibling standalone render_referee.py by path (same skill dir). Returns the module,
    or None if it cannot be imported — then V5 degrades to not_captured, never a fake pass."""
    try:
        p = Path(__file__).resolve().parent / "render_referee.py"
        spec = importlib.util.spec_from_file_location("rr_render_referee", str(p))
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:  # pragma: no cover - defensive; a broken sibling never fails the harness
        return None


def _v5_not_captured(report_format: str, reason: str) -> dict:
    return {
        "leg": "V5", "verdict": "not_captured", "label": "judged",
        "inference_independent": False, "blocking": False,
        "evidence": f"render referee unavailable for format {report_format!r}: {reason} — "
                    "not_captured (never a fake pass)",
    }


def leg_v5(report_format: str, output_path: str | None = None) -> dict:
    if report_format == "office":
        return _leg_v5_office(output_path)
    # HTML — wire the standalone Playwright render-referee module in for the REAL leg under the venv.
    rr = _import_render_referee()
    if rr is None or output_path is None:
        return _v5_not_captured(
            "html", "render_referee module unimportable" if rr is None else "no output path"
        )
    try:
        cap = rr.playwright_capability()
    except Exception as exc:  # pragma: no cover - defensive
        return _v5_not_captured("html", f"capability probe failed: {type(exc).__name__}")
    if not cap.get("available"):
        return _v5_not_captured("html", cap.get("reason") or "Playwright not usable in this interpreter")
    receipt = rr.render_referee(output_path)
    # `diagnostics` is NOT part of the strict legReceipt (additionalProperties:false) — drop it.
    receipt.pop("diagnostics", None)
    return receipt


def _leg_v5_office(output_path: str | None) -> dict:
    """Office V5 — render the docx via LibreOffice `soffice`→image when present, else not_captured.
    A genuine mid-render crash is PROBE_ERROR (never a fake pass). No network; the only writes are
    scratch images in a private tempdir, cleaned up."""
    import shutil

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice or output_path is None:
        return _v5_not_captured(
            "office", "no LibreOffice/soffice on PATH" if not soffice else "no output path"
        )
    import subprocess
    import tempfile

    try:
        src = safe_read_path(output_path)
    except HarnessError as exc:
        return _v5_not_captured("office", f"input error: {exc}")
    tmpdir = tempfile.mkdtemp(prefix="rr-soffice-")
    try:
        proc = subprocess.run(  # noqa: S603 - fixed argv, no shell; soffice resolved via which()
            [soffice, "--headless", "--convert-to", "png", "--outdir", tmpdir, str(src)],
            capture_output=True, timeout=90, check=False,
        )
        produced = sorted(Path(tmpdir).glob("*.png"))
        if proc.returncode != 0 or not produced:
            return {
                "leg": "V5", "verdict": "PROBE_ERROR", "label": "judged",
                "inference_independent": False, "blocking": False,
                "evidence": f"LibreOffice render of {src.name} produced no image (rc={proc.returncode}) "
                            "— PROBE_ERROR, never a fake pass",
            }
        return {
            "leg": "V5", "verdict": "pass", "label": "judged",
            "inference_independent": False, "blocking": False, "repeat_count": 1,
            "judge_fingerprint": f"render-referee/libreoffice@{Path(soffice).name}",
            "evidence": f"LibreOffice rendered {src.name} -> {produced[0].name} "
                        f"({produced[0].stat().st_size} bytes); layout captured",
        }
    except Exception as exc:  # a genuine crash mid-render -> PROBE_ERROR, never a fake pass
        return {
            "leg": "V5", "verdict": "PROBE_ERROR", "label": "judged",
            "inference_independent": False, "blocking": False,
            "evidence": f"LibreOffice render crashed: {type(exc).__name__}: {exc}",
        }
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ─────────────────────────────────────────────────────────────────────────────
# Leg V6 — manifest-completeness / value-coverage (the partition audit)
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_binding_element(output_root: Element, output_text: str | None, anchor: dict):
    """Resolve a manifest binding's anchor to a harness Element — element_id / simple '#id' via
    find_by_id, and a COMPOUND css_selector via the shared rr_anchor's stable structural PATH mapped
    onto harness's own tree (P2 #8: an id-less bound slot addressed by a compound selector must not
    be silently skipped). Returns None if the anchor names no node (or a compound anchor is given
    without the raw output text needed to resolve it)."""
    kind = anchor.get("kind")
    value = anchor.get("value", "")
    if kind == "element_id":
        return find_by_id(output_root, value)
    if kind == "css_selector":
        m = _SIMPLE_ID_SELECTOR.match(value or "")
        if m:
            return find_by_id(output_root, m.group(1))
        if value and output_text is not None:
            try:
                target = rr_anchor.document_path(output_text, anchor)
            except rr_anchor.AnchorError:
                return None
            for el in iter_elements(output_root):
                if _element_path(el) == target:
                    return el
    return None


def leg_v6(output_root: Element, manifest: dict, new_data: dict,
           output_text: str | None = None) -> tuple[dict, list[str]]:
    domain = value_domain(new_data)
    blocking_failures: list[str] = []
    advisory: list[str] = []

    # (1) BLOCKING: a value slot the manifest calls surgical/regenerate that the OUTPUT presents
    # as frozen/unbound while still carrying a dataset value = frozen-misclassification staleness.
    for b in manifest.get("bindings", []):
        if b.get("class") not in ("surgical", "regenerate"):
            continue
        anchor = b.get("anchor", {})
        kind = anchor.get("kind")
        if kind not in ("element_id", "css_selector"):
            continue
        # a compound css_selector needs the raw output text to resolve via rr_anchor; without it
        # (an unusual API call) skip rather than false-flag a "vanished" slot.
        if kind == "css_selector" and not _SIMPLE_ID_SELECTOR.match(anchor.get("value") or "") \
                and output_text is None:
            continue
        node = _resolve_binding_element(output_root, output_text, anchor)
        if node is None:
            blocking_failures.append("bound slot {} vanished from output".format(anchor.get("value")))
            continue
        out_role = node.attr.get("data-role")
        out_bound = "data-bind" in node.attr
        if out_role == "frozen" or (b["class"] == "surgical" and not out_bound and out_role != "regenerate"):
            node_typed = typed_values_in(node)
            carried = sorted(tv for tv in node_typed if tv in domain)
            if carried:
                blocking_failures.append(
                    "{}: manifest class={} but output presents it frozen/unbound while carrying "
                    "dataset value(s) {} — silent staleness".format(anchor.get("value"), b["class"], carried)
                )

    # (2) ADVISORY (hard rule §4): any value-shaped token in a frozen region force-demotes to
    # needs-review. Non-blocking (the clean control's marketing "100%" / stamp date live here).
    for el in iter_elements(output_root):
        if el.attr.get("data-role") == "frozen":
            for (t, v) in typed_values_in(el):
                advisory.append(
                    f"frozen node #{el.id or el.tag} bears value-shaped literal ({t} {v}) — advisory "
                    "needs-review"
                )

    if blocking_failures:
        return ({
            "leg": "V6", "verdict": "fail", "label": "proven",
            "inference_independent": True, "blocking": True,
            "evidence": "coverage failure (ML-free): " + "; ".join(blocking_failures),
        }, advisory)
    return ({
        "leg": "V6", "verdict": "pass", "label": "proven",
        "inference_independent": True, "blocking": True,
        "evidence": f"every value slot covered by a binding; {len(advisory)} advisory frozen-region "
                    "literal(s) surfaced as needs-review (non-blocking)",
    }, advisory)


# ─────────────────────────────────────────────────────────────────────────────
# Period-coherence — every rendered label + value provenance period matches the new period
# ─────────────────────────────────────────────────────────────────────────────

def leg_period(output_root: Element, manifest: dict, new_data: dict) -> dict:
    canonical = normalize_value(new_data.get("period", ""), "period")
    if canonical is None:
        # fall back to the modal provenance period declared in the manifest
        periods = [
            b["provenance"]["source_period"]
            for b in manifest.get("bindings", [])
            if b.get("provenance", {}).get("source_period")
        ]
        canonical = normalize_value(periods[0], "period") if periods else None
    if canonical is None:
        return {
            "leg": "period-coherence", "verdict": "PROBE_ERROR", "label": "proven",
            "inference_independent": True, "blocking": True,
            "evidence": "no canonical reporting period resolvable from new-data or manifest",
        }

    failures: list[str] = []

    # rendered period labels (data-shape="period" nodes + their text)
    for el in iter_elements(output_root):
        if el.attr.get("data-shape") == "period":
            for p in find_periods(text_content(el, skip=NON_RENDERED_TAGS)):
                if p != canonical:
                    failures.append(
                        f"rendered period label #{el.id or el.tag}={p} disagrees with new period {canonical}"
                    )

    # value/asset provenance periods carried in the output (incl. PBI screenshot/figure)
    for el in iter_elements(output_root):
        for attr_name in ("data-period", "data-source-period"):
            raw = el.attr.get(attr_name)
            if raw:
                p = normalize_value(raw, "period")
                if p is not None and p != canonical:
                    failures.append(
                        f"#{el.id or el.tag} {attr_name}={raw} ({p}) disagrees with new period {canonical}"
                    )
        # PBI screenshot alt-text period (a stale-period figure caption)
        if el.tag == "img" and el.attr.get("data-source") == "power-bi-screenshot":
            for p in find_periods(el.attr.get("alt", "")):
                if p != canonical:
                    failures.append(
                        f"#{el.id or el.tag} screenshot alt-text period {p} disagrees with new period {canonical}"
                    )

    if failures:
        return {
            "leg": "period-coherence", "verdict": "fail", "label": "proven",
            "inference_independent": True, "blocking": True,
            "evidence": "period incoherence (ML-free): " + "; ".join(sorted(set(failures))),
        }
    return {
        "leg": "period-coherence", "verdict": "pass", "label": "proven",
        "inference_independent": True, "blocking": True,
        "evidence": f"every rendered label + value/PBI provenance period matches new period {canonical}",
    }


# ══════════════════════════════════════════════════════════════════════════════
# OFFICE (OOXML / docx) lane — the format-detected analogue of every leg above, over the OPC
# container. Keys on the SHARED OOXML anchor grammar (scripts/rr_anchor.py). The HTML lane above is
# untouched; this lane is a parallel orchestration reusing the shared helpers (typed value-space,
# _scan_taint, value_domain, compute_gate, the receipt build/validate).
# ══════════════════════════════════════════════════════════════════════════════

_OFFICE_HEADING_STYLES = frozenset(
    ["Title", "Heading1", "Heading2", "Heading3", "Heading4", "Heading5", "Heading6"]
)

# Parts that legitimately differ template->output (so the V2 frozen-complement byte check EXCLUDES
# them): document.xml (masked canonical-diff instead), the metadata/comment parts scrubbed pre-emit,
# and every raster / chart / embedded-data-cache part (forced-`regenerate` per spec §4 — a
# transplanted binary can't be proven data-free; a leak there is V4's job, not V2's).
_OFFICE_MUTABLE_PARTS = frozenset(
    ["word/document.xml", "docProps/core.xml", "docProps/app.xml", "word/comments.xml"]
)
_OFFICE_MUTABLE_PREFIXES = ("word/media/", "word/charts/", "word/embeddings/")


def _olocal(tag: str) -> str:
    return rr_anchor.ooxml_local(tag)


class OfficeContainer:
    """A decoded OPC (.docx) package: every part name -> raw bytes (opened in-memory, never a second
    path read). `document_xml` is the main story part every structural leg walks."""

    __slots__ = ("parts",)

    def __init__(self, parts: dict) -> None:
        self.parts = parts

    @property
    def document_xml(self) -> bytes:
        return self.parts.get("word/document.xml", b"")


def _office_parts_from_bytes(raw: bytes, source: str, require_document: bool,
                             max_parts: int = 8000) -> dict:
    if raw[:2] != b"PK":
        raise HarnessError(f"{source}: not an OPC/zip (.docx) container")
    parts: dict = {}
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                if len(parts) >= max_parts:  # zip-bomb guard (part-count cap)
                    break
                parts[info.filename] = zf.read(info.filename)
    except zipfile.BadZipFile as exc:
        raise HarnessError(f"{source}: corrupt zip: {exc}")
    if require_document and "word/document.xml" not in parts:
        raise HarnessError(f"{source}: no word/document.xml part (not a Word .docx?)")
    return parts


def _read_office_container(raw_path: str) -> OfficeContainer:
    resolved = safe_read_path(raw_path)
    return OfficeContainer(
        _office_parts_from_bytes(resolved.read_bytes(), str(resolved), require_document=True)
    )


def _reject_xml_dtd(data: bytes) -> None:
    """XXE / billion-laughs defense (stdlib floor — mirrors rr_anchor / infer_office). A valid OOXML
    part NEVER carries a DTD, so any DOCTYPE/ENTITY is a hostile template treated as data, refused
    before xml.etree expands anything."""
    low = data.lower()
    if b"<!doctype" in low or b"<!entity" in low:
        raise HarnessError("DOCTYPE/DTD/ENTITY in an OOXML part is rejected (XXE / entity-expansion defense)")


def _office_body(document_xml: bytes) -> ET.Element:
    _reject_xml_dtd(document_xml)
    try:
        root = ET.fromstring(document_xml)
    except ET.ParseError as exc:
        raise HarnessError(f"word/document.xml is not well-formed XML: {exc}")
    for node in root.iter():
        if _olocal(node.tag) == "body":
            return node
    raise HarnessError("word/document.xml has no w:body element")


def _office_walk(el: ET.Element, steps: tuple):
    """Yield (element, absolute_path) for `el` and every descendant. The path is the tuple of
    (local_name, nth) steps from the w:body element down (EXCLUDING body — body itself is ()),
    computed with the SHARED indexing rule (rr_anchor.ooxml_sibling_index / ooxml_local), so it
    equals rr_anchor.ooxml_document_path(...) for the same node — the two masks/locators align."""
    yield el, steps
    children = list(el)
    qnames = [c.tag for c in children]
    for i, child in enumerate(children):
        idx = rr_anchor.ooxml_sibling_index(qnames, i)
        yield from _office_walk(child, steps + ((_olocal(child.tag), idx),))


def _office_run_text(el: ET.Element) -> str:
    """The concatenated text of a run/paragraph/cell subtree (every descendant w:t; w:tab/w:br give
    a separating space). Mirrors rr_anchor.OoxmlNode.text() / infer_office._run_text."""
    parts: list[str] = []
    for node in el.iter():
        ln = _olocal(node.tag)
        if ln == "t":
            parts.append(node.text or "")
        elif ln in ("tab", "br", "cr"):
            parts.append(" ")
    return "".join(parts)


def _office_run_typed(el: ET.Element) -> set:
    return extract_typed_values(_office_run_text(el))


def _office_block_typed(el: ET.Element) -> set:
    """Typed values at PARAGRAPH/CELL (joined-run) granularity — the joined text of every descendant
    w:t with no separators between sibling runs, so a figure SPLIT across sibling w:r (which the
    per-run scan misses) is detected as one token (P3 #13 / P1 #9)."""
    return extract_typed_values(_office_run_text(el))


def _office_joined_block_texts(document_xml: bytes) -> list:
    """The run-joined text of each paragraph/cell in document.xml (adjacency preserved). Used by the
    Office V4 corpus (P3 #13) so a value split across sibling runs is scanned as one token; returns
    [] on a malformed part (the raw-bytes fallback still covers it)."""
    try:
        body = _office_body(document_xml)
    except HarnessError:
        return []
    out: list = []
    for el, _ in _office_walk(body, ()):
        if _olocal(el.tag) in ("p", "tc"):
            t = _office_run_text(el)
            if t:
                out.append(t)
    return out


def _office_is_heading(p: ET.Element) -> bool:
    for child in list(p):
        if _olocal(child.tag) != "pPr":
            continue
        for gc in list(child):
            if _olocal(gc.tag) == "pStyle":
                for k, v in gc.attrib.items():
                    if _olocal(k) == "val" and v in _OFFICE_HEADING_STYLES:
                        return True
    return False


def _office_typed_values(document_xml: bytes) -> set:
    body = _office_body(document_xml)
    vals: set = set()
    for el, _ in _office_walk(body, ()):
        if _olocal(el.tag) == "r":
            vals.update(extract_typed_values(_office_run_text(el)))
    return vals


def _office_anchor_paths(manifest: dict, document_xml: bytes, classes: tuple) -> set:
    """Resolve every binding whose class is in `classes` to its absolute structural path tuple
    (via the shared resolver). An anchor that no longer resolves is skipped — V2/V3/V6 then
    legitimately surface any change there rather than silently masking it."""
    paths: set = set()
    for b in manifest.get("bindings", []):
        if b.get("class") not in classes:
            continue
        anchor = b.get("anchor", {})
        if anchor.get("kind") != "ooxml_path":
            continue
        try:
            paths.add(rr_anchor.ooxml_document_path(document_xml, anchor))
        except rr_anchor.AnchorError:
            pass
    return paths


def _path_str(path: tuple) -> str:
    return rr_anchor.ooxml_path_value([(local, n) for (local, n) in path])


# ── Office V1 — value accuracy (recompute 2nd path + anchor + set-membership + cross-slot) ────

def leg_v1_office(template_document_xml: bytes, output_document_xml: bytes, manifest: dict,
                  new_data: dict) -> dict:
    values = new_data.get("values", {})
    output_typed = _office_typed_values(output_document_xml)

    expr_bindings: dict = {}
    for b in manifest.get("bindings", []):
        dq = b.get("data_query")
        if dq and dq.get("expression") and b.get("anchor", {}).get("kind") == "ooxml_path":
            expr_bindings.setdefault(dq["expression"], []).append(b)

    anchor_failures: list[str] = []
    membership_failures: list[str] = []
    crossslot_failures: list[str] = []

    for key, spec in values.items():
        expected = normalize_value(spec["value"], spec["type"])
        if expected is None:
            continue
        if (spec["type"], expected) not in output_typed:
            membership_failures.append(
                "{}={!r} recomputed from new source appears nowhere in output".format(key, spec["value"])
            )

    # locate-at-anchor + cross-slot keyed on the data_query.expression on BOTH sides (P3 #14).
    for expr, bindings_for_expr in expr_bindings.items():
        spec = values.get(expr)
        if spec is None:
            continue
        vtype = spec["type"]
        expected = normalize_value(spec["value"], vtype)
        if expected is None:
            continue
        expected_token = (vtype, expected)

        slot_values: list[str] = []
        for b in bindings_for_expr:
            node = rr_anchor.ooxml_try_resolve(output_document_xml, b["anchor"])
            if node is None:
                anchor_failures.append(
                    "anchor {} for {} missing from output".format(b["anchor"]["value"], expr)
                )
                continue
            node_typed = extract_typed_values(node.text())
            typed_of_kind = sorted(v for (t, v) in node_typed if t == vtype)
            if expected_token not in node_typed:
                anchor_failures.append(
                    "{} carries {} not {!r}".format(
                        b["anchor"]["value"], typed_of_kind or "no value", spec["value"]
                    )
                )
            if typed_of_kind:
                slot_values.append(typed_of_kind[0])

        distinct = sorted(set(slot_values))
        if len(distinct) > 1:
            crossslot_failures.append(
                f"{expr} bound to {len(slot_values)} slots that disagree: {distinct}"
            )

    fired = anchor_failures or membership_failures or crossslot_failures
    verdict = "fail" if fired else "pass"
    evidence_parts: list[str] = []
    if anchor_failures:
        evidence_parts.append("anchor: " + "; ".join(anchor_failures))
    if membership_failures:
        evidence_parts.append("set-membership(ML-free): " + "; ".join(membership_failures))
    if crossslot_failures:
        evidence_parts.append("cross-slot(ML-free): " + "; ".join(crossslot_failures))
    if not evidence_parts:
        evidence_parts.append(
            f"all {len(values)} recomputed values landed at their OOXML anchors and appear "
            "in-document; no cross-slot disagreement"
        )
    return {
        "leg": "V1", "verdict": verdict, "label": "proven",
        "inference_independent": False, "blocking": True,
        "evidence": " | ".join(evidence_parts),
    }


# ── Office V2 — frozen-complement over the docx parts + masked document.xml canonical diff ─────

def _office_canonical_tokens(body: ET.Element, excluded: set) -> list[str]:
    """A canonical token stream of word/document.xml. A bound (surgical/regenerate/needs-review)
    anchor path is masked to a single `[ANCHOR:local]` placeholder (its value/inner is legitimately
    mutable). `w:rsid*` revision attributes are canonicalized away (revision noise, not frozen
    chrome). Mirrors the HTML canonical_tokens exactly."""
    toks: list[str] = []

    def rec(e: ET.Element, st: tuple) -> None:
        local = _olocal(e.tag)
        if st != () and st in excluded:
            toks.append(f"[ANCHOR:{local}]")
            return
        attrs = " ".join(
            f"{_olocal(k)}={v!r}"
            for k, v in sorted(e.attrib.items(), key=lambda kv: kv[0])
            if not _olocal(k).lower().startswith("rsid")
        )
        toks.append(f"<{local} {attrs}>")
        t = normalize_ws(e.text or "")
        if t:
            toks.append("#text:" + t)
        children = list(e)
        qnames = [c.tag for c in children]
        for i, c in enumerate(children):
            idx = rr_anchor.ooxml_sibling_index(qnames, i)
            rec(c, st + ((_olocal(c.tag), idx),))
            tail = normalize_ws(c.tail or "")
            if tail:
                toks.append("#tail:" + tail)
        toks.append(f"</{local}>")

    rec(body, ())
    return toks


def _office_frozen_part_diffs(tmpl: OfficeContainer, out: OfficeContainer) -> list[str]:
    diffs: list[str] = []
    for name in sorted(set(tmpl.parts) | set(out.parts)):
        if name in _OFFICE_MUTABLE_PARTS or any(name.startswith(p) for p in _OFFICE_MUTABLE_PREFIXES):
            continue
        t = tmpl.parts.get(name)
        o = out.parts.get(name)
        if t is None:
            diffs.append(f"frozen part {name!r} ADDED in output")
        elif o is None:
            diffs.append(f"frozen part {name!r} REMOVED from output")
        elif t != o:
            diffs.append(f"frozen part {name!r} changed bytes ({len(t)}->{len(o)})")
    return diffs


def leg_v2_office(tmpl: OfficeContainer, out: OfficeContainer, manifest: dict) -> dict:
    part_diffs = _office_frozen_part_diffs(tmpl, out)
    excluded = _office_anchor_paths(manifest, tmpl.document_xml, _MUTABLE_CLASSES)
    t_toks = _office_canonical_tokens(_office_body(tmpl.document_xml), excluded)
    o_toks = _office_canonical_tokens(_office_body(out.document_xml), excluded)
    doc_equal = t_toks == o_toks
    if not part_diffs and doc_equal:
        return {
            "leg": "V2", "verdict": "pass", "label": "proven",
            "inference_independent": True, "blocking": True,
            "evidence": f"frozen complement identical outside {len(excluded)} bound anchor(s): "
                        f"{len(tmpl.parts)} OPC part(s) byte-frozen (metadata/media/embeddings excluded), "
                        f"document.xml canonically matched ({len(t_toks)} tokens)",
        }
    if part_diffs:
        return {
            "leg": "V2", "verdict": "fail", "label": "proven",
            "inference_independent": True, "blocking": True,
            "evidence": "frozen OPC part(s) changed outside bound anchors: " + "; ".join(part_diffs),
        }
    n = min(len(t_toks), len(o_toks))
    idx = n
    for i in range(n):
        if t_toks[i] != o_toks[i]:
            idx = i
            break
    t_tok = t_toks[idx] if idx < len(t_toks) else "(end)"
    o_tok = o_toks[idx] if idx < len(o_toks) else "(end)"
    return {
        "leg": "V2", "verdict": "fail", "label": "proven",
        "inference_independent": True, "blocking": True,
        "evidence": f"document.xml changed outside bound anchors at token {idx}: template {t_tok[:120]!r} "
                    f"!= output {o_tok[:120]!r}",
    }


# ── Office V3 — coarse count cross-check (ML-free) + tag-skeleton isomorphism ──────────────────

def _office_counts(body: ET.Element) -> dict:
    counts = {"paragraph": 0, "table": 0, "row": 0, "cell": 0, "drawing": 0, "heading": 0}
    for el, _ in _office_walk(body, ()):
        local = _olocal(el.tag)
        if local == "p":
            counts["paragraph"] += 1
            if _office_is_heading(el):
                counts["heading"] += 1
        elif local == "tbl":
            counts["table"] += 1
        elif local == "tr":
            counts["row"] += 1
        elif local == "tc":
            counts["cell"] += 1
        elif local == "drawing":
            counts["drawing"] += 1
    return counts


def _office_skeleton(body: ET.Element, excluded: set) -> list[str]:
    out: list[str] = []

    def rec(e: ET.Element, st: tuple) -> None:
        children = list(e)
        qnames = [c.tag for c in children]
        for i, c in enumerate(children):
            cst = st + ((_olocal(c.tag), idx_i(qnames, i)),)
            out.append(_olocal(c.tag))
            if cst not in excluded:
                rec(c, cst)

    def idx_i(qnames: list, i: int) -> int:
        return rr_anchor.ooxml_sibling_index(qnames, i)

    rec(body, ())
    return out


def leg_v3_office(tmpl: OfficeContainer, out: OfficeContainer, manifest: dict) -> dict:
    tbody = _office_body(tmpl.document_xml)
    obody = _office_body(out.document_xml)
    tc = _office_counts(tbody)
    oc = _office_counts(obody)
    tc["parts"] = len(tmpl.parts)
    oc["parts"] = len(out.parts)
    diffs = [f"{k}: template={tc[k]} output={oc[k]}" for k in tc if tc[k] != oc[k]]
    if diffs:
        return {
            "leg": "V3", "verdict": "fail", "label": "proven",
            "inference_independent": False, "blocking": True,
            "evidence": "rule-based coarse structural cross-check (ML-free) fired — count mismatch: "
                        + "; ".join(diffs),
        }
    excluded = _office_anchor_paths(manifest, tmpl.document_xml, _MUTABLE_CLASSES)
    if _office_skeleton(tbody, excluded) != _office_skeleton(obody, excluded):
        return {
            "leg": "V3", "verdict": "fail", "label": "proven",
            "inference_independent": False, "blocking": True,
            "evidence": "coarse counts match but OOXML tag-skeleton isomorphism failed (structure reordered)",
        }
    return {
        "leg": "V3", "verdict": "pass", "label": "proven",
        "inference_independent": False, "blocking": True,
        "evidence": f"coarse OOXML counts (ML-free) match {tc}; tag-skeleton isomorphic",
    }


# ── Office V4 — taint egress over the DECODED docx container (unzip EVERY part) ────────────────

def _xml_all_text_and_attrs(data: bytes) -> str:
    """All element text + tails + attribute values of an XML part (the identity-string surface). A
    part that is not well-formed (or carries a rejected DTD) falls back to the raw decoded bytes so
    a literal is never missed."""
    try:
        _reject_xml_dtd(data)
        root = ET.fromstring(data)
    except Exception:
        return data.decode("utf-8", "replace")
    parts: list[str] = []
    for el in root.iter():
        if el.text:
            parts.append(el.text)
        if el.tail:
            parts.append(el.tail)
        for v in el.attrib.values():
            if v:
                parts.append(v)
    return " ".join(parts)


def _xml_first_text(data: bytes, local: str) -> str | None:
    if not data:
        return None
    try:
        _reject_xml_dtd(data)
        root = ET.fromstring(data)
    except Exception:
        return None
    for el in root.iter():
        if _olocal(el.tag) == local:
            return el.text
    return None


# Recognized BINARY blobs (by MAGIC BYTES, not extension) with no stdlib-scannable text — raster
# images, fonts, OLE compound objects, nested zips, embedded PDFs. Everything else is treated as
# text-bearing and folded into the V4 corpus (P2 round-4: the scan surface must match rezip's
# pass-through surface, which is extension-agnostic — so a .vml textbox or an altChunk .htm/.rtf/.txt
# payload carrying an old-client literal cannot escape V4 by having a non-.xml extension).
_BINARY_MAGIC = (
    b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"BM",              # PNG / JPEG / GIF / BMP
    b"wOFF", b"wOF2", b"\x00\x01\x00\x00", b"OTTO", b"ttcf",  # WOFF / WOFF2 / TTF / OTF / TTC fonts
    b"\xd0\xcf\x11\xe0",                                      # OLE compound (word/embeddings/*.bin)
    b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08",              # zip archive (unrecognized)
    b"%PDF",                                                  # embedded PDF
)


def _is_binary_media(data: bytes) -> bool:
    """True if the part is a recognized binary blob (image/font/OLE/zip/pdf) with no stdlib-scannable
    text — keyed on MAGIC BYTES, not extension, so a text part with an odd extension (legacy VML
    `.vml`, altChunk `.htm`/`.rtf`/`.txt`, unknown) is still scanned by V4 rather than mis-bucketed."""
    return bool(data) and data.startswith(_BINARY_MAGIC)


def _candidate_text_decodings(data: bytes) -> list:
    """Decode a non-binary text part under several candidate encodings so an old-client literal in a
    non-utf-8 part (UTF-16 altChunk/VML, cp1252/latin-1) cannot evade the V4 scan (P1 round-5). V4 is
    a scan, so extra candidate corpora only add coverage, never false positives. `latin-1` is a
    lossless single-byte superset (catches any 8-bit encoding's ASCII/latin literals); the UTF-16
    decodes collapse the NUL interleaving that would otherwise hide a double-byte literal."""
    out: list = []
    seen: set = set()

    def _add(s: str) -> None:
        if s and s not in seen:
            seen.add(s)
            out.append(s)

    if data[:3] == b"\xef\xbb\xbf":
        _add(data.decode("utf-8-sig", "replace"))
    elif data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        _add(data.decode("utf-16", "replace"))
    else:
        _add(data.decode("utf-8", "replace"))
    _add(data.decode("latin-1", "replace"))  # lossless single-byte superset
    if b"\x00" in data[:128]:  # BOM-less UTF-16-ish -> recover both byte orders
        for enc in ("utf-16-le", "utf-16-be"):
            try:
                _add(data.decode(enc, "replace"))
            except Exception:
                pass
    return out


def _decoded_container_office(container: OfficeContainer, _depth: int = 0) -> tuple:
    """The DECODED docx container V4 scans (spec §6.5): unzip EVERY part and scan word/document.xml,
    docProps/core.xml+app.xml, word/comments.xml, word/charts/*.xml, and — recursing into the nested
    OPC zip — word/embeddings/*.xlsx (the embedded chart-data cache that carries the client's full
    OLD dataset as raw unformatted figures). Returns (corpus_text, typed_value_set)."""
    text_parts: list[str] = []
    typed: set = set()
    for name, data in container.parts.items():
        low = name.lower()
        if low.endswith((".xml", ".rels")):
            t = _xml_all_text_and_attrs(data)
            text_parts.append(t)
            typed.update(extract_typed_values(t))
            # P2 (round-3 security): ElementTree DROPS XML comments, so an old-client literal hidden
            # in a <!-- --> comment inside a WELL-FORMED OOXML part would parse fine and be silently
            # dropped, escaping V4 (the office-lane analogue of the round-1 HTML comment-leak P0). Fold
            # the RAW decoded bytes UNCONDITIONALLY (not just on a parse exception) as a raw-byte
            # backstop so comments / processing-instructions are scanned — parity with the HTML lane.
            # P1 (round-6): the comment raw-backstop must be ENCODING-agnostic like the non-XML branch
            # below — a literal in an XML comment inside a UTF-16 OOXML part would mojibake under a
            # utf-8-only decode and escape V4 (the round-3-comment x round-5-encoding seam). Fold every
            # candidate decoding, identical to the non-binary branch.
            for raw in _candidate_text_decodings(data):
                text_parts.append(raw)
                typed.update(extract_typed_values(raw))
            # P3 #13 — the space-joining corpus above breaks a value SPLIT across sibling w:t/w:r
            # (e.g. `$1,284,`+`500` -> "$1,284, 500"). For the story part, ALSO fold in each
            # paragraph/cell's run-joined text (adjacency preserved) so the split value is scanned
            # as one token by both the typed extractor and the raw-number backstop.
            if low.endswith("document.xml"):
                for joined in _office_joined_block_texts(data):
                    text_parts.append(joined)
                    typed.update(extract_typed_values(joined))
        elif low.endswith((".xlsx", ".xlsm", ".docx", ".pptx")) and _depth < 2:
            try:
                nested = OfficeContainer(
                    _office_parts_from_bytes(data, name, require_document=False)
                )
                st, sty = _decoded_container_office(nested, _depth + 1)
                text_parts.append(st)
                typed.update(sty)
            except Exception:  # a corrupt nested cache still gets a raw-literal scan
                blob = data.decode("latin-1", "replace")
                text_parts.append(blob)
                typed.update(extract_typed_values(blob))
        elif not _is_binary_media(data):
            # P2 (round-4): the V4 scan surface must NOT be extension-keyed — fold every non-binary
            # text part in by MAGIC BYTES (legacy VML `.vml`, altChunk `.htm`/`.rtf`/`.txt`, unknown).
            # P1 (round-5): and NOT encoding-keyed either — a UTF-16 altChunk/VML part mojibakes under
            # utf-8 and would evade V4, so fold every candidate decoding (BOM-sniffed unicode + a
            # lossless latin-1 superset + BOM-less UTF-16) so a literal in any common encoding is caught.
            for blob in _candidate_text_decodings(data):
                text_parts.append(blob)
                typed.update(extract_typed_values(blob))
        # else: a recognized binary blob (image/font/OLE/zip/pdf) — no stdlib OCR; not text-scanned
        # (the documented local-execution limitation, shared with rasters; such nodes are forced to
        # `regenerate` upstream where classified).
    return " ".join(text_parts), typed


_RE_BARE_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def _raw_numbers(corpus: str) -> set:
    """Canonical BARE numeric tokens in the corpus — the embedded-xlsx cache stores figures raw
    (e.g. `1284500`), which the typed extractor (currency/percent/grouped) never captures."""
    out: set = set()
    for m in _RE_BARE_NUMBER.finditer(corpus):
        c = canon_number(m.group())
        if c is not None:
            out.add(c)
    return out


def _office_embedded_cache_figures(container: OfficeContainer) -> set:
    """Every distinct raw figure carried in the template's embedded chart-data caches
    (word/embeddings/*.xlsx — nested OPC zips). These are the client's OLD dataset stored as raw,
    unformatted numbers that do NOT appear in the refreshed rendered body, so — unlike the visible
    document.xml story values — they are safe to taint by default (they can only survive as a stale
    old-dataset leak, never a legitimate same-period value)."""
    figures: set = set()
    for name, data in container.parts.items():
        low = name.lower()
        if name.startswith("word/embeddings/") and low.endswith((".xlsx", ".xlsm")):
            try:
                _, typed = _decoded_container_office(
                    OfficeContainer(_office_parts_from_bytes(data, name, require_document=False)),
                    _depth=1,
                )
            except Exception:
                continue
            blob_numbers = _raw_numbers(data.decode("latin-1", "replace"))
            for (_t, c) in typed:
                figures.add(c)
            figures |= blob_numbers
    return figures


def derive_taint_office(container: OfficeContainer, override: dict | None) -> dict:
    """Default Office taint = the OLD template's docProps identity strings (Author / lastModifiedBy
    / Title / Company) — direct identity leaks that must always be scrubbed — PLUS (P1 #3) the
    embedded chart-data-cache value literals (word/embeddings/*.xlsx: the client's OLD dataset as
    raw figures). The cache figures are wired in BY DEFAULT, not only via a caller override, because
    they never appear in a legitimate same-period refresh (unlike the visible document.xml story
    values, which are deliberately NOT auto-tainted to avoid false-positiving on a same-period
    refresh). `override` still fully replaces the derived dict when supplied."""
    if override:
        return dict(override)
    out: dict = {}
    core = container.parts.get("docProps/core.xml", b"")
    app = container.parts.get("docProps/app.xml", b"")
    for local, key in (("creator", "old_author"), ("lastModifiedBy", "old_last_modified_by"),
                       ("title", "old_title")):
        v = _xml_first_text(core, local)
        if v and v.strip():
            out[key] = v.strip()
    comp = _xml_first_text(app, "Company")
    if comp and comp.strip():
        out["old_company"] = comp.strip()
    for i, figure in enumerate(sorted(_office_embedded_cache_figures(container))):
        out[f"old_embedded_cache_value_{i}"] = figure
    return out


def leg_v4_office(container: OfficeContainer, taint: dict) -> dict:
    corpus, corpus_typed = _decoded_container_office(container)
    return _v4_leg(
        corpus, corpus_typed, taint,
        "the decoded docx container (document.xml + docProps + comments.xml + charts + embedded xlsx, decoded)",
        corpus_numbers=_raw_numbers(corpus),
    )


# ── Office V6 — manifest-completeness / value-coverage (the partition audit, ML-free) ─────────

def leg_v6_office(output_document_xml: bytes, manifest: dict, new_data: dict) -> tuple:
    domain = value_domain(new_data)
    covered = _office_anchor_paths(manifest, output_document_xml, ("surgical", "regenerate"))
    body = _office_body(output_document_xml)
    blocking_failures: list[str] = []
    advisory: list[str] = []

    for el, path in _office_walk(body, ()):
        local = _olocal(el.tag)
        if local == "r":
            tv = _office_run_typed(el)
            if not tv or path in covered:
                continue
            loc = _path_str(path)
            # a dataset value in an UNBOUND (frozen) region = frozen-misclassification silent
            # staleness. (period tokens are period-coherence's job, excluded here to avoid false
            # positives on a legitimately-frozen period label.)
            domain_hits = sorted(tv_i for tv_i in tv if tv_i in domain and tv_i[0] != "period")
            if domain_hits:
                blocking_failures.append(
                    f"{loc}: value-shaped dataset value(s) {domain_hits} carried in an unbound/frozen "
                    "region — coverage failure (silent staleness)"
                )
            else:
                for (t, v) in sorted(tv):
                    advisory.append(
                        f"frozen-region run {loc} bears value-shaped literal ({t} {v}) — advisory needs-review"
                    )
        elif local == "p":
            # P1 #9 — paragraph joined-run granularity: a dataset value SPLIT across sibling w:r (no
            # single run carries it whole) escapes the per-run scan above. Compare the paragraph's
            # joined-run typed values against the union of its per-run typed values; a domain value
            # present ONLY in the joined text, in an unbound paragraph, is silent staleness too.
            if path in covered:
                continue
            joined_tv = _office_block_typed(el)
            if not joined_tv:
                continue
            per_run: set = set()
            for r in el.iter():
                if _olocal(r.tag) == "r":
                    per_run |= _office_run_typed(r)
            split_only = joined_tv - per_run
            split_hits = sorted(tv_i for tv_i in split_only if tv_i in domain and tv_i[0] != "period")
            if split_hits:
                blocking_failures.append(
                    f"{_path_str(path)}: dataset value(s) {split_hits} SPLIT across sibling runs in an "
                    "unbound/frozen paragraph — coverage failure (silent staleness)"
                )
            elif split_only:
                # P2 (round 2): mirror the per-run else-advisory (~:1717-1721) at joined-run
                # granularity -- a split literal that is NOT itself a domain hit still must not ship
                # silently (guarantee (b)); only a genuine domain hit escalates to blocking above.
                for (t, v) in sorted(split_only):
                    advisory.append(
                        f"frozen-region paragraph {_path_str(path)} bears run-split value-shaped "
                        f"literal ({t} {v}) — advisory needs-review"
                    )

    for b in manifest.get("bindings", []):
        if b.get("class") not in ("surgical", "regenerate"):
            continue
        anchor = b.get("anchor", {})
        if anchor.get("kind") != "ooxml_path":
            continue
        if not rr_anchor.ooxml_exists(output_document_xml, anchor):
            blocking_failures.append(f"bound slot {anchor.get('value')!r} vanished from output")

    if blocking_failures:
        return ({
            "leg": "V6", "verdict": "fail", "label": "proven",
            "inference_independent": True, "blocking": True,
            "evidence": "coverage failure (ML-free): " + "; ".join(blocking_failures),
        }, advisory)
    return ({
        "leg": "V6", "verdict": "pass", "label": "proven",
        "inference_independent": True, "blocking": True,
        "evidence": f"every value slot covered by a binding; {len(advisory)} advisory frozen-region "
                    "literal(s) surfaced as needs-review (non-blocking)",
    }, advisory)


# ── Office period-coherence — rendered labels + binding provenance match the new period ────────

def leg_period_office(output_document_xml: bytes, manifest: dict, new_data: dict) -> dict:
    canonical = normalize_value(new_data.get("period", ""), "period")
    if canonical is None:
        periods = [
            b["provenance"]["source_period"]
            for b in manifest.get("bindings", [])
            if b.get("provenance", {}).get("source_period")
        ]
        canonical = normalize_value(periods[0], "period") if periods else None
    if canonical is None:
        return {
            "leg": "period-coherence", "verdict": "PROBE_ERROR", "label": "proven",
            "inference_independent": True, "blocking": True,
            "evidence": "no canonical reporting period resolvable from new-data or manifest",
        }

    failures: list[str] = []
    body = _office_body(output_document_xml)
    for el, path in _office_walk(body, ()):
        if _olocal(el.tag) != "r":
            continue
        for p in find_periods(_office_run_text(el)):
            if p != canonical:
                failures.append(
                    f"rendered period label {_path_str(path)}={p} disagrees with new period {canonical}"
                )
    for b in manifest.get("bindings", []):
        sp = b.get("provenance", {}).get("source_period")
        if sp:
            p = normalize_value(sp, "period")
            if p is not None and p != canonical:
                ident = b.get("node_id") or b.get("anchor", {}).get("value")
                failures.append(
                    f"binding {ident} source_period {sp} ({p}) disagrees with new period {canonical}"
                )

    if failures:
        return {
            "leg": "period-coherence", "verdict": "fail", "label": "proven",
            "inference_independent": True, "blocking": True,
            "evidence": "period incoherence (ML-free): " + "; ".join(sorted(set(failures))),
        }
    return {
        "leg": "period-coherence", "verdict": "pass", "label": "proven",
        "inference_independent": True, "blocking": True,
        "evidence": f"every rendered label + binding provenance period matches new period {canonical}",
    }


# ── Office pre-emit purge expectation (metadata / comments / tracked changes) → manual_residue ──

def _office_purge_residue(container: OfficeContainer) -> list[str]:
    residue: list[str] = []
    if "word/comments.xml" in container.parts:
        residue.append(
            "pre-emit purge expectation: word/comments.xml is still present in the output "
            "(comment purge incomplete)"
        )
    doc = container.document_xml
    if b"<w:ins" in doc or b"<w:del" in doc:
        residue.append(
            "pre-emit purge expectation: unaccepted tracked changes (w:ins/w:del) survive in "
            "word/document.xml"
        )
    core = container.parts.get("docProps/core.xml", b"")
    for local, label in (("creator", "dc:creator"), ("lastModifiedBy", "cp:lastModifiedBy")):
        v = _xml_first_text(core, local)
        if v and v.strip():
            residue.append(
                f"pre-emit metadata-scrub expectation: docProps/core.xml {label} is non-empty "
                f"({v.strip()!r})"
            )
    return residue


# ── Office orchestration (mirrors run_legs / build_receipt; reuses the shared helpers) ─────────

def run_legs_office(tmpl: OfficeContainer, out: OfficeContainer, manifest: dict, new_data: dict,
                    taint: dict, output_path: str, disabled: set) -> tuple:
    manual_residue: list[str] = []
    results: dict = {}
    tdoc = tmpl.document_xml
    odoc = out.document_xml

    def guarded(name: str, fn) -> None:
        if name in disabled:
            blk, indep = _LEG_META[name]
            results[name] = _neutered(name, blk, indep)
            return
        try:
            results[name] = fn()
        except Exception as exc:  # PROBE_ERROR != pass
            blk, indep = _LEG_META[name]
            results[name] = {
                "leg": name, "verdict": "PROBE_ERROR", "label": "proven",
                "inference_independent": indep, "blocking": blk,
                "evidence": f"harness crash while running {name} (office): {type(exc).__name__}: {exc}",
            }

    guarded("V1", lambda: leg_v1_office(tdoc, odoc, manifest, new_data))
    guarded("V2", lambda: leg_v2_office(tmpl, out, manifest))
    guarded("V3", lambda: leg_v3_office(tmpl, out, manifest))
    guarded("V4", lambda: leg_v4_office(out, taint))
    guarded("V5", lambda: leg_v5("office", output_path))

    if "V6" in disabled:
        blk, indep = _LEG_META["V6"]
        results["V6"] = _neutered("V6", blk, indep)
    else:
        try:
            v6, advisory = leg_v6_office(odoc, manifest, new_data)
            results["V6"] = v6
            manual_residue.extend(advisory)
        except Exception as exc:
            results["V6"] = {
                "leg": "V6", "verdict": "PROBE_ERROR", "label": "proven",
                "inference_independent": True, "blocking": True,
                "evidence": f"harness crash while running V6 (office): {type(exc).__name__}: {exc}",
            }

    guarded("period-coherence", lambda: leg_period_office(odoc, manifest, new_data))

    try:
        manual_residue.extend(_office_purge_residue(out))
    except Exception:  # a residue-probe crash never fails the harness (advisory only)
        pass

    return [results[name] for name in LEG_ORDER], manual_residue


def _build_receipt_office(template_path: str, output_path: str, manifest: dict, new_data: dict,
                          taint_override: dict | None, disabled: set, ttl_seconds: int) -> dict:
    tmpl = _read_office_container(template_path)
    out = _read_office_container(output_path)
    taint = derive_taint_office(tmpl, taint_override)
    legs, manual_residue = run_legs_office(
        tmpl, out, manifest, new_data, taint, output_path, disabled
    )
    return {
        "receipt_version": RECEIPT_VERSION,
        "run_id": uuid.uuid4().hex,
        "format": "office",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ttl_seconds": ttl_seconds,
        "env_fingerprint": env_fingerprint(),
        "overall_gate": compute_gate(legs),
        "manual_residue": manual_residue,
        "legs": legs,
    }


def _detect_format(raw_path: str) -> str:
    """html vs office, by extension then magic (`PK\\x03\\x04` zip => office). Path-guarded."""
    p = safe_read_path(raw_path)
    ext = p.suffix.lower()
    if ext in (".docx", ".docm"):
        return "office"
    if ext in (".html", ".htm", ".xhtml"):
        return "html"
    with open(p, "rb") as fh:
        head = fh.read(4)
    return "office" if head[:2] == b"PK" else "html"


# ─────────────────────────────────────────────────────────────────────────────
# Orchestration
# ─────────────────────────────────────────────────────────────────────────────

LEG_ORDER = ["V1", "V2", "V3", "V4", "V5", "V6", "period-coherence"]

# P1 #5 — the must-fail-mutant leg-disable knob is a TEST-ONLY footgun, not a production CLI
# option: a disabled leg proves nothing about fidelity, so it must never be reachable on a real
# run. Honoring `disabled_legs` requires this env flag to be set (the test suites set it); absent
# it, the CLI refuses --disable-leg and the Python API ignores the request (legs run normally).
_DISABLE_LEG_ENV = "RR_HARNESS_ENABLE_DISABLE_LEG"


def _disable_allowed() -> bool:
    return bool(os.environ.get(_DISABLE_LEG_ENV))


def _sanitized_disabled(disabled_legs) -> set:
    """The effective disabled-leg set: honored only under the test-only env flag; otherwise empty
    (a neutered leg can never silently ship on a production run)."""
    return set(disabled_legs) if _disable_allowed() else set()


def _neutered(leg_name: str, blocking: bool, inference_independent: bool) -> dict:
    # P1 #5 — a neutered leg reports verdict "disabled" (NEVER "pass"): it proves nothing, so it
    # must not read as fidelity-OK, and compute_gate forces the overall gate off PASS on any
    # disabled leg (a blocking disabled leg → FAIL). This is the mutant that shows the enabled leg
    # has real teeth, without ever letting the mutant itself green-light a delivery.
    return {
        "leg": leg_name, "verdict": "disabled", "label": "proven",
        "inference_independent": inference_independent, "blocking": blocking,
        "evidence": "LEG DISABLED via the test-only must-fail knob — verdict 'disabled' (never a "
                    "pass); the overall gate is forced off PASS. This is the neutered mutant that "
                    "proves the enabled leg has real teeth.",
    }


_LEG_META = {
    "V1": (True, False), "V2": (True, True), "V3": (True, False), "V4": (True, True),
    "V5": (False, False), "V6": (True, True), "period-coherence": (True, True),
}


def run_legs(template_root: Element, output_root: Element, manifest: dict, new_data: dict,
             taint: dict[str, str], report_format: str, disabled: set[str],
             template_text: str, output_path: str | None = None,
             output_text: str | None = None) -> tuple[list[dict], list[str]]:
    manual_residue: list[str] = []
    results: dict[str, dict] = {}

    def guarded(name: str, fn):
        if name in disabled:
            blk, indep = _LEG_META[name]
            results[name] = _neutered(name, blk, indep)
            return
        try:
            results[name] = fn()
        except Exception as exc:  # PROBE_ERROR != pass (a crash never reads as fidelity-OK)
            blk, indep = _LEG_META[name]
            results[name] = {
                "leg": name, "verdict": "PROBE_ERROR", "label": "proven",
                "inference_independent": indep, "blocking": blk,
                "evidence": f"harness crash while running {name}: {type(exc).__name__}: {exc}",
            }

    guarded("V1", lambda: leg_v1(template_root, output_root, manifest, new_data))
    guarded("V2", lambda: leg_v2(template_root, output_root, manifest, template_text))
    guarded("V3", lambda: leg_v3(template_root, output_root, manifest, template_text))
    guarded("V4", lambda: leg_v4(output_root, taint, output_text))
    guarded("V5", lambda: leg_v5(report_format, output_path))

    if "V6" in disabled:
        blk, indep = _LEG_META["V6"]
        results["V6"] = _neutered("V6", blk, indep)
    else:
        try:
            v6, advisory = leg_v6(output_root, manifest, new_data, output_text)
            results["V6"] = v6
            manual_residue.extend(advisory)
        except Exception as exc:
            results["V6"] = {
                "leg": "V6", "verdict": "PROBE_ERROR", "label": "proven",
                "inference_independent": True, "blocking": True,
                "evidence": f"harness crash while running V6: {type(exc).__name__}: {exc}",
            }

    guarded("period-coherence", lambda: leg_period(output_root, manifest, new_data))

    return [results[name] for name in LEG_ORDER], manual_residue


def compute_gate(legs: list[dict]) -> str:
    # A blocking leg that FAILED, crashed (PROBE_ERROR), or was neutered (disabled — P1 #5) forces
    # a hard FAIL; a disabled non-blocking leg still forbids PASS (falls through to PARTIAL below).
    blocking_bad = any(
        leg["blocking"] and leg["verdict"] in ("fail", "PROBE_ERROR", "disabled") for leg in legs
    )
    if blocking_bad:
        return "FAIL"
    non_pass = any(leg["verdict"] != "pass" for leg in legs)
    return "PARTIAL" if non_pass else "PASS"


def env_fingerprint() -> str:
    raw = "python={}|platform={}|harness={}".format(
        sys.version.replace("\n", " "), platform.platform(), RECEIPT_VERSION
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_receipt(template_root: Element, output_root: Element, manifest: dict, new_data: dict,
                  taint: dict[str, str], report_format: str, disabled: set[str],
                  ttl_seconds: int, template_text: str, output_path: str | None = None,
                  output_text: str | None = None) -> dict:
    legs, manual_residue = run_legs(
        template_root, output_root, manifest, new_data, taint, report_format, disabled,
        template_text, output_path, output_text,
    )
    receipt = {
        "receipt_version": RECEIPT_VERSION,
        "run_id": uuid.uuid4().hex,
        "format": report_format,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ttl_seconds": ttl_seconds,
        "env_fingerprint": env_fingerprint(),
        "overall_gate": compute_gate(legs),
        "manual_residue": manual_residue,
        "legs": legs,
    }
    return receipt


def run_harness(template_path: str, output_path: str, manifest_path: str, new_data_path: str,
                taint: dict | None = None, disabled_legs=(), report_format: str | None = None,
                ttl_seconds: int = DEFAULT_TTL_SECONDS) -> dict:
    """Python API. Format-detects html vs office (docx) and runs the matching leg implementations;
    `report_format` overrides. Returns a fidelity-receipt dict (already schema-validated)."""
    manifest = load_json(manifest_path)
    new_data = load_json(new_data_path)
    if not isinstance(manifest, dict) or not isinstance(new_data, dict):
        raise HarnessError("manifest and new-data must each be a JSON object")

    fmt = report_format
    if fmt is None:
        out_fmt = _detect_format(output_path)
        tmpl_fmt = _detect_format(template_path)
        if out_fmt != tmpl_fmt:
            raise HarnessError(
                f"format mismatch: template detected as {tmpl_fmt!r} but output as {out_fmt!r}; "
                "pass --report-format to override"
            )
        fmt = out_fmt
    if fmt not in ("html", "office"):
        raise HarnessError(f"unsupported report format: {fmt!r}")

    # P1 #5 — leg disabling is honored only under the test-only env flag; on a real run the request
    # is dropped so a neutered leg can never silently green-light a delivery.
    disabled = _sanitized_disabled(disabled_legs)

    if fmt == "office":
        receipt = _build_receipt_office(
            template_path, output_path, manifest, new_data, taint, disabled, ttl_seconds
        )
    else:
        template_text = read_text(template_path)
        output_text = read_text(output_path)
        template_root = parse_html(template_text)
        output_root = parse_html(output_text)
        taint_dict = derive_taint(template_text, taint)
        receipt = build_receipt(
            template_root, output_root, manifest, new_data, taint_dict, fmt,
            disabled, ttl_seconds, template_text, output_path, output_text,
        )

    errors = validate_receipt(receipt)
    if errors:  # fail-closed: a receipt that does not validate is not a receipt
        raise HarnessError("emitted receipt failed schema validation: " + "; ".join(errors))
    return receipt


# ─────────────────────────────────────────────────────────────────────────────
# Minimal JSON-Schema validator (Draft-2020-12 subset used by fidelity-receipt.schema.json).
# Genuinely validates the emitted receipt against the frozen schema file.
# ─────────────────────────────────────────────────────────────────────────────

def _schema_path() -> Path:
    return Path(__file__).resolve().parents[2] / "knowledge" / "fidelity-receipt.schema.json"


def _resolve_ref(ref: str, root: dict) -> dict:
    node: object = root
    for part in ref.lstrip("#/").split("/"):
        node = node[part]  # type: ignore[index]
    return node  # type: ignore[return-value]


_TYPEMAP = {
    "object": dict, "array": list, "string": str, "integer": int,
    "number": (int, float), "boolean": bool,
}


def _type_ok(inst: object, t) -> bool:
    types = t if isinstance(t, list) else [t]
    for name in types:
        py = _TYPEMAP[name]
        if name == "integer":
            if isinstance(inst, int) and not isinstance(inst, bool):
                return True
        elif name == "number":
            if isinstance(inst, (int, float)) and not isinstance(inst, bool):
                return True
        elif isinstance(inst, py) and not (py is dict and isinstance(inst, bool)):
            if name == "boolean" and not isinstance(inst, bool):
                continue
            if isinstance(inst, py):
                return True
    return False


def _matches(inst: object, schema: dict, root: dict) -> bool:
    return not _walk(inst, schema, root, "$")


def _walk(inst: object, schema: dict, root: dict, path: str) -> list[str]:
    errs: list[str] = []
    if "$ref" in schema:
        schema = _resolve_ref(schema["$ref"], root)
    if "type" in schema and not _type_ok(inst, schema["type"]):
        errs.append("{}: expected type {}, got {}".format(path, schema["type"], type(inst).__name__))
        return errs
    if "const" in schema and inst != schema["const"]:
        errs.append("{}: expected const {!r}".format(path, schema["const"]))
    if "enum" in schema and inst not in schema["enum"]:
        errs.append("{}: {!r} not in enum {}".format(path, inst, schema["enum"]))
    if "pattern" in schema and isinstance(inst, str) and not re.search(schema["pattern"], inst):
        errs.append("{}: {!r} does not match {!r}".format(path, inst, schema["pattern"]))
    if "minimum" in schema and isinstance(inst, (int, float)) and inst < schema["minimum"]:
        errs.append("{}: {} < minimum {}".format(path, inst, schema["minimum"]))
    if "minLength" in schema and isinstance(inst, str) and len(inst) < schema["minLength"]:
        errs.append("{}: length {} < minLength {}".format(path, len(inst), schema["minLength"]))
    if isinstance(inst, dict):
        props = schema.get("properties", {})
        for r in schema.get("required", []):
            if r not in inst:
                errs.append(f"{path}: missing required property {r!r}")
        if schema.get("additionalProperties") is False:
            for k in inst:
                if k not in props:
                    errs.append(f"{path}: additional property {k!r} not allowed")
        for k, subschema in props.items():
            if k in inst:
                errs.extend(_walk(inst[k], subschema, root, path + "." + k))
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]:
            errs.append("{}: {} items < minItems {}".format(path, len(inst), schema["minItems"]))
        if "items" in schema:
            for i, item in enumerate(inst):
                errs.extend(_walk(item, schema["items"], root, f"{path}[{i}]"))
        if "contains" in schema:
            if not any(_matches(item, schema["contains"], root) for item in inst):
                errs.append(f"{path}: no item matches 'contains'")
    if "not" in schema and _matches(inst, schema["not"], root):
        errs.append(f"{path}: instance matches 'not' schema (forbidden)")
    for sub in schema.get("allOf", []):
        if "if" in sub:
            if _matches(inst, sub["if"], root):
                errs.extend(_walk(inst, sub.get("then", {}), root, path))
            elif "else" in sub:
                errs.extend(_walk(inst, sub["else"], root, path))
        else:
            errs.extend(_walk(inst, sub, root, path))
    if "if" in schema:
        if _matches(inst, schema["if"], root):
            errs.extend(_walk(inst, schema.get("then", {}), root, path))
        elif "else" in schema:
            errs.extend(_walk(inst, schema["else"], root, path))
    return errs


def validate_receipt(receipt: dict) -> list[str]:
    schema = json.loads(_schema_path().read_text(encoding="utf-8"))
    return _walk(receipt, schema, schema, "$")


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="harness.py",
        description="Run the report-regeneration fidelity harness (6 legs + period-coherence) "
                    "and emit a schema-valid fidelity-receipt.",
    )
    p.add_argument("--template", required=True, help="template report (HTML or docx)")
    p.add_argument("--output", required=True, help="regenerated output to verify (HTML or docx)")
    p.add_argument("--manifest", required=True, help="binding-manifest.json")
    p.add_argument("--new-data", dest="new_data", required=True, help="new dataset JSON")
    p.add_argument("--format", default="json", choices=["json"],
                   help="receipt serialization format (json)")
    p.add_argument("--report-format", dest="report_format", default=None,
                   choices=["html", "office"],
                   help="override the auto-detected report format (html|office). "
                        "Default: detect by extension/magic (PK zip => office).")
    p.add_argument("--taint", default=None,
                   help="optional taint-dictionary JSON (old-artifact literals). Default: derive "
                        "from the template's documented TAINT block.")
    p.add_argument("--disable-leg", dest="disable_leg", action="append", default=[],
                   metavar="LEG", choices=LEG_ORDER,
                   help="neuter a leg (TEST-ONLY must-fail mutant knob — refused unless the "
                        f"{_DISABLE_LEG_ENV} env flag is set; a disabled leg forces the gate off "
                        "PASS and is never a production option). Repeatable.")
    p.add_argument("--ttl", type=int, default=DEFAULT_TTL_SECONDS, help="receipt TTL seconds")
    p.add_argument("--pretty", action="store_true", help="pretty-print the receipt JSON")
    return p


def main(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    if args.disable_leg and not _disable_allowed():
        # P1 #5 — --disable-leg is a test-only footgun; refuse it on a production run rather than
        # silently emitting a green receipt for a neutered leg.
        print(json.dumps({
            "ok": False,
            "error": "--disable-leg is a test-only must-fail knob and is refused unless the "
                     f"{_DISABLE_LEG_ENV} env flag is set (it would neuter a blocking fidelity leg)",
        }))
        print(f"[error] --disable-leg refused: set {_DISABLE_LEG_ENV}=1 only in a test harness",
              file=sys.stderr)
        return 2
    try:
        taint = None
        if args.taint:
            loaded = load_json(args.taint)
            if not isinstance(loaded, dict):
                raise HarnessError("--taint must be a JSON object of {label: literal}")
            taint = loaded
        receipt = run_harness(
            args.template, args.output, args.manifest, args.new_data,
            taint=taint, disabled_legs=args.disable_leg, report_format=args.report_format,
            ttl_seconds=args.ttl,
        )
    except HarnessError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        print(f"[error] {exc}", file=sys.stderr)
        return 2
    print(json.dumps(receipt, indent=2 if args.pretty else None))
    gate = receipt["overall_gate"]
    return 1 if gate == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
