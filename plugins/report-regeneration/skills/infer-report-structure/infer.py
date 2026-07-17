#!/usr/bin/env python3
"""
infer.py — infer-report-structure (report-regeneration HTML pipeline, stage 1).

Parses an HTML report template into a Report Structure Graph (RSG): a format-neutral
ordered tree whose node order is load-bearing (document order — V2 diff and V3 isomorphism
depend on it). The RSG is an ADDRESSING-AND-VERIFICATION structure, NEVER a generator
(core-architecture-spec.md §2). Every node carries a stable anchor (element id / CSS
selector — NEVER a char-offset), an inferred role, a rebind class, a confidence, a
provenance record (method/source/source_period/pbi_route), and the output of the pinned,
non-inference, deterministic data-shaped-literal detector.

The data-shaped-literal detector is the load-bearing, inference-INDEPENDENT half: it flags
currency/number/date/percent/unit/known-entity shapes deterministically, and its output
drives the EARNED-frozen rule (§4) — any data-shaped literal in a candidate-`frozen` node
FORCE-DEMOTES it to `needs-review`, regardless of classifier confidence. Semantic role/class
labeling here is a rule-based STUB (method: "rule-based") that reads the fixture's explicit
data-* annotation scheme; there is no live LLM call.

Usage:
    python3 infer.py --in <template.html> --out <rsg.json>
    python3 infer.py --in <template.html> --out <rsg.json> --format json
    python3 infer.py --in <template.html> --out <rsg.json> --template-id acme-quarterly

Exit codes:
    0 — success (RSG built, schema-valid, written to --out)
    2 — usage / path-guard / read / parse / schema-validation error (message on stderr; with
        --format json a best-effort JSON error object is printed to stdout so a caller parsing
        stdout never gets truncated/ambiguous JSON)

Design constraints (binding, per the I1-infer brief):
    - Stdlib only: argparse, html.parser, json, os, re, sys, typing. Runs on Python 3.9.6 with
      NO pip installs. lxml/selectolax are OPTIONAL acceleration via a graceful try/import that
      changes nothing when absent (the html.parser tree build is the sole code path).
    - No network. No subprocess.
    - Path-guarded: --in/--out reject any '..' traversal component and any path that escapes the
      repo root (mirrors plugins/ravenclaude-core/skills/svg-report-lint/lint.py's
      _repo_root()/_safe_path(): an absolute path INSIDE the repo is allowed; an absolute or
      symlink ESCAPE is rejected).
    - from __future__ import annotations (3.9-safe): no runtime X|Y unions, no match statements.
    - Codes to the SCHEMAS. The emitted RSG is validated against knowledge/rsg.schema.json before
      it is written; an invalid build refuses to write and exits 2.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser
from typing import Any

# ── optional acceleration (graceful, non-load-bearing) ───────────────────────────────────────
# The stdlib html.parser tree build below is the SOLE parse path (guaranteed on 3.9.6, no pip).
# A present lxml/selectolax is recorded for the summary only; its absence changes nothing.
_ACCEL: str | None = None
try:  # pragma: no cover - environment-dependent
    import selectolax  # type: ignore  # noqa: F401

    _ACCEL = "selectolax"
except Exception:  # pragma: no cover
    try:
        import lxml  # type: ignore  # noqa: F401

        _ACCEL = "lxml"
    except Exception:
        _ACCEL = None

RSG_SCHEMA_VERSION = "1.0.0"
DEFAULT_CONFIDENCE_THRESHOLD = 0.6

# Void (self-closing) HTML elements — no end tag, never pushed onto the open-element stack.
_VOID_TAGS = frozenset(
    [
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    ]
)

# Tags whose text is code/markup, NOT report data — skipped by the data-shaped-literal detector.
_OPAQUE_TEXT_TAGS = frozenset(["style", "script"])

# Recognized structural/semantic chrome tags — used to keep confidence high for ordinary chrome.
_STRUCTURAL_TAGS = frozenset(
    [
        "html", "head", "body", "header", "footer", "main", "section", "article", "aside",
        "nav", "div", "span", "p", "a", "ul", "ol", "li", "table", "thead", "tbody", "tfoot",
        "tr", "td", "th", "caption", "h1", "h2", "h3", "h4", "h5", "h6", "figure", "figcaption",
        "strong", "em", "b", "i", "small", "title", "meta", "style", "link", "br", "hr",
    ]
)


class InferError(Exception):
    """Raised for any path-guard, read, parse, or schema-validation failure (never a bare OSError)."""


# ── path safety (mirrors svg-report-lint/lint.py _repo_root()/_safe_path()) ───────────────────

def _repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    root = here
    for _ in range(12):
        if os.path.isfile(os.path.join(root, ".repo-layout.json")) or os.path.isfile(
            os.path.join(root, "AGENTS.md")
        ):
            return root
        parent = os.path.dirname(root)
        if parent == root:
            break
        root = parent
    # Fallback: this file lives at plugins/report-regeneration/skills/infer-report-structure/infer.py
    return os.path.abspath(os.path.join(here, "..", "..", "..", ".."))


def _safe_path(raw: str, *, must_exist: bool) -> str:
    """Resolve `raw` and reject traversal / repo-escape. Absolute paths INSIDE the repo are
    allowed (svg-report-lint convention); '..' and any escape (incl. via symlink) are rejected."""
    if not raw:
        raise InferError("empty path")
    if ".." in raw.replace("\\", "/").split("/"):
        raise InferError(f"path contains a '..' traversal component: {raw!r}")
    repo = os.path.realpath(_repo_root())
    # os.path.join discards cwd when `raw` is absolute — so an absolute-inside-repo path resolves
    # to itself and passes; a relative path resolves against cwd, exactly like svg-report-lint.
    resolved = os.path.realpath(os.path.join(os.getcwd(), raw))
    if resolved != repo and not resolved.startswith(repo + os.sep):
        raise InferError(f"path escapes the repo root: {resolved!r}")
    if must_exist and not os.path.isfile(resolved):
        raise InferError(f"file not found: {raw!r} (resolved {resolved})")
    return resolved


# ── the deterministic, non-inference data-shaped-literal detector (load-bearing) ──────────────
#
# Flags currency / number / date / percent / unit / known-entity SHAPES. It is intentionally
# blind to meaning: it cannot (and must not try to) tell "100%" the marketing tagline from
# "100%" the KPI, or "Fiscal Year 2024" the static citation from a data-bound period. That is
# the whole point — a data-shaped literal in a candidate-`frozen` node force-demotes it to
# `needs-review` regardless of what a semantic classifier believes (§4). Independent of the
# LLM-accuracy ceiling.

_MONTHS = (
    "January|February|March|April|May|June|July|August|September|October|November|December"
)

_DETECTORS = [
    # currency: a currency symbol immediately preceding a number ("$4,821,300", "£1,200.50")
    ("currency", re.compile(r"[$£€¥]\s?\d[\d,]*(?:\.\d+)?")),
    # percent: a (optionally signed) number followed by '%' ("+12.4%", "18.7%", "100%")
    ("percent", re.compile(r"[+\-−]?\d+(?:\.\d+)?\s?%")),
    # date (month-name form): "April 4, 2025", "April 4 2025"
    ("date", re.compile(r"\b(?:" + _MONTHS + r")\s+\d{1,2},?\s+\d{4}\b")),
    # date (ISO form): "2025-04-04"
    ("date", re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),
    # year: a bare 4-digit 19xx/20xx ("2024", "since 1998", "Fiscal Year 2024")
    ("year", re.compile(r"\b(?:19|20)\d{2}\b")),
    # number (grouped thousands): "1,203,400" — a value shape, not a lone small integer
    ("number", re.compile(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b")),
    # number (magnitude-suffixed): "$18.2M", "18.2M", "4.8B", "500K"
    ("unit", re.compile(r"\b\d+(?:\.\d+)?\s?(?:K|M|B|bn|mn|k)\b")),
    # unit (number + explicit unit): "500px", "12 USD", "3.5kg"
    ("unit", re.compile(r"\b\d+(?:\.\d+)?\s?(?:px|pt|USD|EUR|GBP|kg|g|GB|MB|TB|kWh)\b")),
    # known-entity (reporting-period token): "Q1 2025", "Q1-2025", "2025-Q1", "FY2024", "FY24"
    ("known-entity", re.compile(r"\bQ[1-4][\s-]?\d{4}\b|\b\d{4}[\s-]?Q[1-4]\b|\bFY\d{2,4}\b")),
]


def detect_data_shaped_literal(text: str) -> dict[str, Any]:
    """Return {"is_data_shaped": bool, "kinds": [...], "matches": [...]} for `text`.

    Deterministic and non-inference. The RSG boolean field `data_shaped_literal` is the
    `is_data_shaped` result. `kinds`/`matches` are diagnostic (not serialized into the node)."""
    if not text:
        return {"is_data_shaped": False, "kinds": [], "matches": []}
    kinds: list[str] = []
    matches: list[str] = []
    for kind, rx in _DETECTORS:
        m = rx.search(text)
        if m:
            if kind not in kinds:
                kinds.append(kind)
            matches.append(m.group(0).strip())
    return {"is_data_shaped": bool(kinds), "kinds": kinds, "matches": matches}


# ── HTML → element tree (stdlib html.parser; document order preserved) ────────────────────────

class _Element:
    __slots__ = ("tag", "attrs", "children", "parent", "text_parts", "type_index")

    def __init__(self, tag: str, attrs: dict[str, str], parent: _Element | None) -> None:
        self.tag = tag
        self.attrs = attrs
        self.children: list[_Element] = []
        self.parent = parent
        self.text_parts: list[str] = []
        self.type_index = 1  # 1-based nth-of-type among same-tag siblings

    def direct_text(self) -> str:
        return "".join(self.text_parts).strip()


class _TreeBuilder(HTMLParser):
    """Builds an ordered _Element tree. Tolerant of unclosed/misnested tags: an end tag pops down
    to its nearest matching open element (or is ignored if none is open)."""

    def __init__(self) -> None:
        # convert_charrefs=True (the 3.5+ default) decodes entities in text — "&amp;" -> "&".
        super().__init__(convert_charrefs=True)
        self.root = _Element("#document", {}, None)
        self._stack: list[_Element] = [self.root]

    def _open(self, tag: str, attrs: list[tuple[str, str | None]]) -> _Element:
        parent = self._stack[-1]
        attr_map: dict[str, str] = {}
        for k, v in attrs:
            # First occurrence wins (HTML5 duplicate-attribute rule); value None -> "".
            if k not in attr_map:
                attr_map[k] = v if v is not None else ""
        el = _Element(tag, attr_map, parent)
        el.type_index = 1 + sum(1 for c in parent.children if c.tag == tag)
        parent.children.append(el)
        return el

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        el = self._open(tag, attrs)
        if tag not in _VOID_TAGS:
            self._stack.append(el)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._open(tag, attrs)  # explicit self-close — never pushed

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self._stack) - 1, 0, -1):  # never pop the synthetic root at index 0
            if self._stack[i].tag == tag:
                del self._stack[i:]
                return
        # no matching open element — ignore (tolerant)

    def handle_data(self, data: str) -> None:
        self._stack[-1].text_parts.append(data)


def _build_tree(html_text: str) -> _Element:
    builder = _TreeBuilder()
    builder.feed(html_text)
    builder.close()
    # Collapse the synthetic #document to a single real root element when there is exactly one
    # (normally <html>); otherwise keep #document as an umbrella root over multiple top-level nodes.
    element_children = list(builder.root.children)
    if len(element_children) == 1:
        root = element_children[0]
        root.parent = None
        return root
    return builder.root


# ── anchor + node-id derivation (stable identity — element id / CSS selector, NEVER char-offset) ─

def _anchor_for(el: _Element) -> dict[str, str]:
    """A stable, re-resolvable node identity. element_id when present; otherwise a CSS selector
    built from nth-of-type steps, anchored at the nearest ancestor carrying an id (shorter and
    more stable than an absolute path). NEVER a raw character offset (RT1-F10)."""
    if el.attrs.get("id"):
        return {"kind": "element_id", "value": el.attrs["id"]}
    segs: list[str] = []
    cur: _Element | None = el
    while cur is not None:
        parent = cur.parent
        if parent is None:
            segs.append(cur.tag)
            break
        segs.append(f"{cur.tag}:nth-of-type({cur.type_index})")
        pid = parent.attrs.get("id")
        if pid:
            segs.append("#" + pid)
            break
        cur = parent
    return {"kind": "css_selector", "value": " > ".join(reversed(segs))}


# ── semantic labeling STUB (rule-based; reads the explicit data-* annotation scheme) ──────────
#
# role/class are assigned by deterministic rules over the fixture's annotation scheme
# (data-role / data-bind / data-shape / data-period / data-section-role / data-source). This is
# a STUB standing in for the model-assisted semantic slot labeling of §2 — method "rule-based",
# no live LLM call. Two SPEC hard rules override any annotation or confidence:
#   (1) rasters and embedded-data-cache nodes are FORCED to `regenerate` (§4 construction rule) —
#       a transplanted binary cannot be proven data-free, so the logo/screenshot/chart images go
#       here even when the fixture annotates them data-role="frozen".
#   (2) a data-shaped literal in a candidate-`frozen` node FORCE-DEMOTES it to `needs-review`
#       regardless of confidence (§4 earned-frozen rule).

_ROLE_STATIC = "static-chrome"


def _is_raster_or_cache(el: _Element) -> bool:
    if el.tag == "img":
        return True
    if el.tag == "script" and el.attrs.get("type", "").lower() in (
        "application/json",
        "application/ld+json",
    ):
        return True  # embedded-data-cache analog (§6.4)
    return False


def _nearest_class_hint(el: _Element) -> str | None:
    """Nearest explicit rebind-class hint on `el` or an ancestor, from data-role /
    data-section-role, mapped to {frozen, surgical, regenerate}. None if unannotated."""
    cur: _Element | None = el
    while cur is not None:
        hint = cur.attrs.get("data-role") or cur.attrs.get("data-section-role")
        if hint in ("frozen", "surgical", "regenerate"):
            return hint
        if hint == "mixed":
            return None  # a mixed section carries no single class; children resolve on their own
        cur = cur.parent
    return None


def _infer_role(el: _Element, shaped: bool) -> str:
    shape = el.attrs.get("data-shape", "")
    cls = el.attrs.get("class", "")
    if el.tag == "img":
        low = (el.attrs.get("data-source", "") + " " + cls + " " + el.attrs.get("alt", "")).lower()
        if "power-bi" in low or "chart" in low or "screenshot" in low or "trend" in low:
            return "chart"
        return "image"
    if shape == "period" or "period" in (el.attrs.get("data-bind", "")):
        return "period-label"
    if el.tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        return "heading"
    if el.tag in ("title", "meta"):
        return "metadata"
    if el.tag in ("td", "th") and (el.attrs.get("data-bind") or shaped):
        return "table-cell"
    if el.attrs.get("data-bind") or shape in ("currency", "percent", "number", "date", "unit"):
        if el.tag in ("td", "th"):
            return "table-cell"
        if "kpi" in cls or "kpi" in el.attrs.get("id", ""):
            return "kpi-value"
        return "kpi-value"
    if el.attrs.get("data-role") == "regenerate" and el.tag in ("p", "div", "span"):
        return "narrative"
    if el.tag in _STRUCTURAL_TAGS:
        return _ROLE_STATIC
    return "unknown"


def _classify(el: _Element, shaped: bool, threshold: float) -> tuple[str, float, str]:
    """Return (class, confidence, method). Applies the two SPEC hard rules last."""
    own = el.attrs.get("data-role", "")
    has_bind = bool(el.attrs.get("data-bind"))
    section_role = el.attrs.get("data-section-role", "")

    # (1) Construction rule — rasters / embedded-data caches are forced to regenerate, always.
    if _is_raster_or_cache(el):
        return "regenerate", 0.95, "native-parse"

    candidate: str | None = None
    confidence = 0.55
    method = "rule-based"

    if own in ("frozen", "surgical", "regenerate"):
        candidate, confidence = own, 0.9
    elif section_role in ("frozen", "surgical", "regenerate"):
        # A section CONTAINER is chrome; treat as a frozen candidate (its data children carry
        # their own classes). A "mixed" section is likewise a frozen chrome container.
        candidate, confidence = "frozen", 0.8
    elif section_role == "mixed":
        candidate, confidence = "frozen", 0.75
    else:
        hint = _nearest_class_hint(el)
        if hint == "regenerate":
            if not shaped and not el.attrs.get("data-bind") and el.tag in (
                "h1", "h2", "h3", "h4", "h5", "h6", "title", "meta"
            ):
                # A section HEADING / metadata element is static chrome even inside a
                # `regenerate` section — it is NOT regenerated *content* (the content nodes
                # carry their OWN data-role="regenerate" and are handled by the `own` branch
                # above). Mirrors the surgical branch's "container chrome inside a surgical
                # section" -> frozen. Without this, a static heading like "Executive Summary"
                # is misclassed `regenerate`, and every downstream stage then tries to rebind a
                # heading that has no data source (the compound-anchor pipeline break, RT1).
                candidate, confidence = "frozen", 0.75
            else:
                candidate, confidence = "regenerate", 0.8  # part of a regenerate slot
        elif hint == "surgical":
            if has_bind:
                candidate, confidence = "surgical", 0.85
            elif shaped:
                # a value-shaped token inside a surgical section with NO binding annotation —
                # exactly the V6 coverage gap; surface it rather than guess a bind.
                candidate, confidence = "needs-review", 0.6
            else:
                candidate, confidence = "frozen", 0.75  # container chrome inside a surgical section
        else:  # frozen ancestor, or wholly unannotated
            if el.tag in _STRUCTURAL_TAGS:
                candidate, confidence = "frozen", 0.85
            else:
                candidate, confidence = "unknown", 0.4

    # (2) Earned-frozen rule — a data-shaped literal in a candidate-frozen node force-demotes it
    #     to needs-review, regardless of classifier confidence.
    if candidate == "frozen" and shaped:
        return "needs-review", confidence, method

    # Sub-threshold confidence -> needs-review (guarantee #2, made mechanical).
    if candidate in ("unknown", None) or confidence < threshold:
        return "needs-review", confidence, method

    return candidate, confidence, method


def _provenance(el: _Element, cls: str, method: str, template_id: str) -> dict[str, Any]:
    data_source = el.attrs.get("data-source", "")
    source = data_source if data_source else template_id
    # source_period: explicit data-period / data-source-period, else null for period-agnostic chrome.
    period = el.attrs.get("data-period") or el.attrs.get("data-source-period") or None
    pbi_route: str | None = None
    low = data_source.lower()
    if "xmla" in low:
        pbi_route = "xmla"
    elif "rest" in low:
        pbi_route = "rest"
    elif "screenshot" in low or "power-bi-screenshot" in low:
        pbi_route = "screenshot"
    prov: dict[str, Any] = {"method": method, "source": source, "source_period": period}
    if pbi_route is not None:
        prov["pbi_route"] = pbi_route
    return prov


# ── RSG build ─────────────────────────────────────────────────────────────────────────────────

def _walk(
    el: _Element,
    template_id: str,
    threshold: float,
    seen_ids: dict[str, int],
    stats: dict[str, Any],
) -> dict[str, Any]:
    shaped_info = (
        {"is_data_shaped": False}
        if el.tag in _OPAQUE_TEXT_TAGS
        else detect_data_shaped_literal(el.direct_text())
    )
    shaped = bool(shaped_info["is_data_shaped"])

    anchor = _anchor_for(el)
    node_id = anchor["value"]
    if node_id in seen_ids:
        seen_ids[node_id] += 1
        node_id = f"{node_id}#{seen_ids[node_id]}"
    else:
        seen_ids[node_id] = 0

    role = _infer_role(el, shaped)
    cls, confidence, method = _classify(el, shaped, threshold)
    provenance = _provenance(el, cls, method, template_id)

    # stats / accounting
    stats["classes"][cls] = stats["classes"].get(cls, 0) + 1
    stats["roles"][role] = stats["roles"].get(role, 0) + 1
    if shaped:
        stats["data_shaped"] += 1
    if cls == "needs-review":
        stats["needs_review"] += 1
    bind = el.attrs.get("data-bind")
    if bind and bind not in stats["data_binds"]:
        stats["data_binds"].append(bind)

    node = {
        "id": node_id,
        "anchor": anchor,
        "role": role,
        "class": cls,
        "confidence": round(confidence, 3),
        "provenance": provenance,
        "data_shaped_literal": shaped,
        "children": [_walk(c, template_id, threshold, seen_ids, stats) for c in el.children],
    }
    return node


def build_rsg(
    html_text: str,
    template_id: str,
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Parse `html_text` into an RSG dict + a stats dict. Pure (no I/O)."""
    tree = _build_tree(html_text)
    stats: dict[str, Any] = {
        "classes": {},
        "roles": {},
        "data_shaped": 0,
        "needs_review": 0,
        "data_binds": [],
        "total_nodes": 0,
        "accelerator": _ACCEL,
    }
    root_node = _walk(tree, template_id, threshold, {}, stats)
    stats["total_nodes"] = sum(stats["classes"].values())
    rsg = {
        "schema_version": RSG_SCHEMA_VERSION,
        "format": "html",
        "template_id": template_id,
        "root": root_node,
    }
    return rsg, stats


# ── minimal JSON-Schema validator (the subset rsg.schema.json uses; stdlib only) ──────────────
#
# Supports: type (incl. type-arrays and "null"), enum, const, required, properties,
# additionalProperties:false, items, pattern, minimum, maximum, minLength, $ref (local
# #/$defs/...), allOf, if/then/else, not. Enough to validate the RSG against rsg.schema.json
# without the third-party `jsonschema` package (no pip installs allowed).

def _json_type_ok(instance: Any, t: str) -> bool:
    if t == "object":
        return isinstance(instance, dict)
    if t == "array":
        return isinstance(instance, list)
    if t == "string":
        return isinstance(instance, str)
    if t == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if t == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if t == "boolean":
        return isinstance(instance, bool)
    if t == "null":
        return instance is None
    return False


def _resolve_ref(ref: str, root_schema: dict[str, Any]) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise InferError(f"unsupported non-local $ref: {ref!r}")
    node: Any = root_schema
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        node = node[part]
    return node


def _validate(instance: Any, schema: Any, root_schema: dict[str, Any], path: str, errors: list[str]) -> None:
    if not isinstance(schema, dict):
        return
    if "$ref" in schema:
        _validate(instance, _resolve_ref(schema["$ref"], root_schema), root_schema, path, errors)
        # $ref appears alone in this schema; no sibling keywords to also apply.
        return

    if "type" in schema:
        types = schema["type"]
        types = types if isinstance(types, list) else [types]
        if not any(_json_type_ok(instance, t) for t in types):
            errors.append(f"{path}: expected type {types}, got {type(instance).__name__}")
            return  # further checks assume the type held

    if "enum" in schema and instance not in schema["enum"]:
        errors.append("{}: {!r} not in enum {}".format(path, instance, schema["enum"]))
    if "const" in schema and instance != schema["const"]:
        errors.append("{}: {!r} != const {!r}".format(path, instance, schema["const"]))

    if isinstance(instance, str):
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append("{}: {!r} does not match pattern {!r}".format(path, instance, schema["pattern"]))
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append("{}: string shorter than minLength {}".format(path, schema["minLength"]))

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append("{}: {} < minimum {}".format(path, instance, schema["minimum"]))
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append("{}: {} > maximum {}".format(path, instance, schema["maximum"]))

    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required property {req!r}")
        if schema.get("additionalProperties", True) is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}: additional property {key!r} not allowed")
        for key, subschema in props.items():
            if key in instance:
                _validate(instance[key], subschema, root_schema, f"{path}.{key}", errors)

    if isinstance(instance, list) and "items" in schema:
        for i, item in enumerate(instance):
            _validate(item, schema["items"], root_schema, f"{path}[{i}]", errors)

    for sub in schema.get("allOf", []):
        _validate(instance, sub, root_schema, path, errors)

    if "if" in schema:
        cond_errors: list[str] = []
        _validate(instance, schema["if"], root_schema, path, cond_errors)
        branch = "then" if not cond_errors else "else"
        if branch in schema:
            _validate(instance, schema[branch], root_schema, path, errors)

    if "not" in schema:
        not_errors: list[str] = []
        _validate(instance, schema["not"], root_schema, path, not_errors)
        if not not_errors:
            errors.append(f"{path}: instance must NOT match the 'not' subschema")


def validate_instance(instance: Any, schema: dict[str, Any]) -> list[str]:
    """Validate `instance` against `schema`; return a list of human-readable error strings ([] == valid)."""
    errors: list[str] = []
    _validate(instance, schema, schema, "$", errors)
    return errors


def load_schema(path: str | None = None) -> dict[str, Any]:
    """Load rsg.schema.json from the plugin knowledge dir (or an explicit path)."""
    if path is None:
        here = os.path.dirname(os.path.abspath(__file__))
        # skills/infer-report-structure/ -> ../../knowledge/rsg.schema.json
        path = os.path.abspath(os.path.join(here, "..", "..", "knowledge", "rsg.schema.json"))
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ── CLI ─────────────────────────────────────────────────────────────────────────────────────

def _summary(rsg: dict[str, Any], stats: dict[str, Any], in_path: str, out_path: str) -> dict[str, Any]:
    return {
        "ok": True,
        "in": in_path,
        "out": out_path,
        "template_id": rsg["template_id"],
        "schema_version": rsg["schema_version"],
        "total_nodes": stats["total_nodes"],
        "classes": stats["classes"],
        "roles": stats["roles"],
        "data_shaped_nodes": stats["data_shaped"],
        "needs_review_nodes": stats["needs_review"],
        "data_binds_found": sorted(stats["data_binds"]),
        "accelerator": stats["accelerator"] or "stdlib(html.parser)",
    }


def _emit_error(message: str, as_json: bool) -> int:
    print(f"[infer] error: {message}", file=sys.stderr)
    if as_json:
        print(json.dumps({"ok": False, "error": message}))
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="infer.py",
        description="Infer a Report Structure Graph (RSG) from an HTML report template.",
    )
    parser.add_argument("--in", dest="in_path", required=True, help="input HTML template (relative or in-repo)")
    parser.add_argument("--out", dest="out_path", required=True, help="output RSG JSON path (relative or in-repo)")
    parser.add_argument("--template-id", dest="template_id", default=None, help="stable template identity (default: input filename stem)")
    parser.add_argument("--confidence-threshold", dest="threshold", type=float, default=DEFAULT_CONFIDENCE_THRESHOLD, help="sub-threshold confidence -> needs-review (default %(default)s)")
    parser.add_argument("--format", dest="fmt", choices=["text", "json"], default="text", help="stdout summary format")
    args = parser.parse_args(argv)
    as_json = args.fmt == "json"

    try:
        in_abs = _safe_path(args.in_path, must_exist=True)
        out_abs = _safe_path(args.out_path, must_exist=False)
    except InferError as exc:
        return _emit_error(str(exc), as_json)

    try:
        with open(in_abs, encoding="utf-8") as fh:
            html_text = fh.read()
    except OSError as exc:
        return _emit_error(f"cannot read input: {exc}", as_json)

    template_id = args.template_id or os.path.splitext(os.path.basename(in_abs))[0]

    try:
        rsg, stats = build_rsg(html_text, template_id, args.threshold)
    except Exception as exc:  # parse/build failure — never a silent crash-as-success
        return _emit_error(f"parse/build failed: {exc}", as_json)

    # Code to the SCHEMA: validate before writing. An invalid build refuses to write.
    try:
        schema = load_schema()
    except Exception as exc:
        return _emit_error(f"cannot load rsg.schema.json: {exc}", as_json)
    schema_errors = validate_instance(rsg, schema)
    if schema_errors:
        return _emit_error(
            "RSG failed schema validation ({} error(s)): {}".format(
                len(schema_errors), "; ".join(schema_errors[:8])
            ),
            as_json,
        )

    try:
        out_dir = os.path.dirname(out_abs)
        if out_dir and not os.path.isdir(out_dir):
            os.makedirs(out_dir, exist_ok=True)
        with open(out_abs, "w", encoding="utf-8") as fh:
            json.dump(rsg, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
    except OSError as exc:
        return _emit_error(f"cannot write output: {exc}", as_json)

    summary = _summary(rsg, stats, args.in_path, args.out_path)
    if as_json:
        print(json.dumps(summary, indent=2))
    else:
        print("[infer] OK — {} nodes -> {}".format(summary["total_nodes"], args.out_path))
        print("  template_id: {}   schema_version: {}   parser: {}".format(
            summary["template_id"], summary["schema_version"], summary["accelerator"]))
        print("  classes: {}".format(summary["classes"]))
        print("  roles: {}".format(summary["roles"]))
        print("  data-shaped nodes: {}   needs-review nodes: {}".format(
            summary["data_shaped_nodes"], summary["needs_review_nodes"]))
        print("  data-binds found ({}): {}".format(
            len(summary["data_binds_found"]), ", ".join(summary["data_binds_found"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
