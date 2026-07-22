#!/usr/bin/env python3
"""
infer_office.py — infer-office (report-regeneration OFFICE/docx pipeline, stage 1).

The Office analogue of skills/infer-report-structure/infer.py. Parses a Word `.docx` template into
a Report Structure Graph (RSG): the SAME format-neutral ordered tree, node taxonomy, and
deterministic data-shaped-literal detector as the HTML lane, but keyed on OOXML anchors instead of
CSS selectors. The RSG is an ADDRESSING-AND-VERIFICATION structure, NEVER a generator
(core-architecture-spec.md §2). Node order is load-bearing (document order — V2 diff and V3
isomorphism depend on it).

Parse path (binding): **stdlib `zipfile` + `xml.etree`** over `word/document.xml`. A doc-order walk
of `w:body` covers paragraphs (`w:p`), runs (`w:r`), tables (`w:tbl`/`w:tr`/`w:tc`), and inline
images (`w:drawing`). `python-docx` is OPTIONAL acceleration via a graceful try/import that changes
NOTHING when absent (the stdlib walk is the sole code path). No network, no live LLM call.

Anchors are produced by — and resolve back through — the SHARED OOXML grammar in
`scripts/rr_anchor.py` (which OWNS the Office anchor contract). Every anchor is `kind:"ooxml_path"`
(the only Office kind the RSG schema admits): a `body`-rooted body-walk path (`body/p[3]/r[1]`), or
a `bookmark(NAME)` path when a `w:bookmarkStart` governs the node. The data-shaped-literal detector
and the schema validator are REUSED verbatim from `infer.py` (single source of truth).

The two SPEC hard rules from §4 fire identically to the HTML lane:
  (1) Construction rule — a `w:drawing`/raster/embedded-binary node is FORCED to `regenerate`
      (a transplanted binary cannot be proven data-free).
  (2) Earned-frozen rule — a data-shaped literal in a candidate-`frozen` node FORCE-DEMOTES it to
      `needs-review`, regardless of classifier confidence.

Semantic role/class labeling here is a deterministic rule-based STUB (method "rule-based") keyed on
OOXML structure (paragraph style, bookmark governance = an explicit data-binding marker, table-cell
membership, drawing presence) — the model-assisted slot labeling of §2 lands in a later stage.

Usage:
    python3 infer_office.py --in <template.docx> --out <rsg.json>
    python3 infer_office.py --in <template.docx> --out <rsg.json> --format json

Exit codes: 0 success; 2 usage / path-guard / read / parse / schema-validation error.

Design constraints (binding): stdlib only (argparse, zipfile, xml.etree, json, re, os, sys).
Python 3.9.6-safe (`from __future__ import annotations`; no `X|Y` unions, no `match`). Path-guarded
(rejects `..` and repo-escape). Codes to the SCHEMA — the RSG is validated against
knowledge/rsg.schema.json before it is written; an invalid build refuses to write and exits 2.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from typing import Any

# ── import the shared HTML-lane detector/validator + the shared OOXML anchor grammar ──────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_SKILLS_DIR = os.path.dirname(_HERE)
_PLUGIN_DIR = os.path.dirname(_SKILLS_DIR)
_INFER_DIR = os.path.join(_SKILLS_DIR, "infer-report-structure")
_SCRIPTS_DIR = os.path.join(_PLUGIN_DIR, "scripts")
for _p in (_INFER_DIR, _SCRIPTS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import infer  # noqa: E402  (reused: detect_data_shaped_literal, validate_instance, load_schema, path guard)
import rr_anchor  # noqa: E402  (shared OOXML anchor grammar — the Office contract owner)

# ── optional acceleration (graceful, non-load-bearing — mirrors infer._ACCEL) ─────────────────
_ACCEL: str | None = None
try:  # pragma: no cover - environment-dependent
    import docx  # type: ignore  # noqa: F401

    _ACCEL = "python-docx"
except Exception:  # pragma: no cover
    _ACCEL = None

RSG_SCHEMA_VERSION = infer.RSG_SCHEMA_VERSION
DEFAULT_CONFIDENCE_THRESHOLD = infer.DEFAULT_CONFIDENCE_THRESHOLD

# Content-bearing OOXML elements the walk emits as RSG nodes (everything else — w:pPr/w:rPr/
# w:sectPr/w:tblPr/… and DrawingML internals — is skipped as a node but still counted for anchor
# indices via the shared rule). A w:drawing is a LEAF image node (not descended into).
_WALK_LOCALS = frozenset(["body", "p", "r", "tbl", "tr", "tc", "drawing"])
_HEADING_STYLES = frozenset(["Title", "Heading1", "Heading2", "Heading3", "Heading4", "Heading5", "Heading6"])

# A period-shaped token (Q1 2025 / 2025-Q1 / FY2024) — used to set/propagate source_period.
_PERIOD_RE = re.compile(r"\bQ[1-4][\s-]?\d{4}\b|\b\d{4}[\s-]?Q[1-4]\b|\bFY\d{2,4}\b")


class OfficeInferError(infer.InferError):
    """Raised for any docx read / zip / parse / schema-validation failure specific to the Office
    lane. Subclasses infer.InferError so callers can catch either lane with one except."""


# ── docx ingestion (stdlib zipfile + xml.etree) ───────────────────────────────────────────────

def read_document_xml(docx_path: str) -> bytes:
    """Return the raw `word/document.xml` bytes from a `.docx` (an OPC/ZIP package). stdlib zipfile
    only — no python-docx. Raises OfficeInferError for a non-zip / missing-part input."""
    try:
        with zipfile.ZipFile(docx_path) as zf:
            try:
                return zf.read("word/document.xml")
            except KeyError:
                raise OfficeInferError(f"{docx_path!r} has no word/document.xml (not a Word .docx?)")
    except zipfile.BadZipFile as exc:
        raise OfficeInferError(f"{docx_path!r} is not a valid .docx zip: {exc}")


def _local(tag: str) -> str:
    return rr_anchor.ooxml_local(tag)


def _run_text(el: ET.Element) -> str:
    """The text of a run/paragraph subtree: concatenation of every descendant w:t (and w:tab/w:br
    contribute a separating space). Mirrors OoxmlNode.text() so producer and resolver agree."""
    parts: list[str] = []
    for node in el.iter():
        ln = _local(node.tag)
        if ln == "t":
            parts.append(node.text or "")
        elif ln in ("tab", "br", "cr"):
            parts.append(" ")
    return "".join(parts)


def _run_own_text(el: ET.Element) -> str:
    """A run's OWN value text = the text of its DIRECT w:t children (not descendants). This is the
    leaf granularity the data-shaped-literal detector runs on — containers (p/tc/…) hold no direct
    w:t and so are never double-flagged for a value that lives in a child run."""
    parts: list[str] = []
    for child in list(el):
        if _local(child.tag) == "t":
            parts.append(child.text or "")
    return "".join(parts)


def _has_drawing(el: ET.Element) -> bool:
    for child in el.iter():
        if _local(child.tag) == "drawing":
            return True
    return False


def _drawing_is_chart(el: ET.Element) -> bool:
    for node in el.iter():
        ln = _local(node.tag)
        if ln == "chart":
            return True
        if ln == "graphicData":
            uri = node.attrib.get("uri", "")
            if "chart" in uri:
                return True
    return False


def _bookmark_name(el: ET.Element) -> str | None:
    for k, v in el.attrib.items():
        if _local(k) == "name":
            return v
    return None


def _paragraph_style(p: ET.Element) -> str | None:
    for child in list(p):
        if _local(child.tag) == "pPr":
            for gc in list(child):
                if _local(gc.tag) == "pStyle":
                    for k, v in gc.attrib.items():
                        if _local(k) == "val":
                            return v
    return None


# ── role / class inference (rule-based STUB; the two SPEC hard rules fire last) ───────────────

def _infer_role(local: str, ctx: dict[str, Any], shaped: bool, is_period: bool) -> str:
    if local == "drawing":
        return "chart" if ctx.get("drawing_is_chart") else "image"
    if local == "tc":
        return "table-cell"
    if local == "p":
        return "heading" if ctx.get("heading_style") else "static-chrome"
    if local == "r":
        if is_period:
            return "period-label"
        if ctx.get("in_tc"):
            return "table-cell"
        if ctx.get("heading_style"):
            return "heading"
        if shaped:
            return "kpi-value"
        return "static-chrome"
    # body / tbl / tr are structural chrome containers
    return "static-chrome"


def _classify(
    local: str, shaped: bool, is_bookmarked: bool, threshold: float
) -> tuple[str, float, str]:
    """Return (class, confidence, method). Applies the two SPEC hard rules last."""
    # (1) Construction rule — a raster/embedded-binary drawing is forced to regenerate, always.
    if local == "drawing":
        return "regenerate", 0.95, "native-parse"

    candidate = "frozen"
    confidence = 0.85
    method = "rule-based"

    if local == "r":
        if shaped and is_bookmarked:
            candidate, confidence = "surgical", 0.85
        elif shaped:
            # a value-shaped token with NO explicit bind marker — surface it (V6 coverage gap).
            candidate, confidence = "needs-review", 0.6
        elif is_bookmarked:
            # a bookmark-marked slot carrying no value — surface it too (a suspicious empty bind).
            candidate, confidence = "needs-review", 0.55
        else:
            candidate, confidence = "frozen", 0.85  # data-free chrome text
    # p / tbl / tr / tc / body containers default to frozen chrome (they hold no direct value text)

    # (2) Earned-frozen rule — a data-shaped literal in a candidate-frozen node force-demotes it.
    if candidate == "frozen" and shaped:
        return "needs-review", confidence, method

    # Sub-threshold confidence -> needs-review (guarantee #2, made mechanical).
    if confidence < threshold:
        return "needs-review", confidence, method

    return candidate, confidence, method


def _provenance(
    local: str,
    shaped: bool,
    is_period: bool,
    current_period: str | None,
    method: str,
    template_id: str,
) -> dict[str, Any]:
    period: str | None = None
    if local == "r" and (shaped or is_period):
        # a value / period-label run belongs to the nearest governing reporting period.
        period = current_period
    return {"method": method, "source": template_id, "source_period": period}


# ── the RSG body-walk (xml.etree; anchors via the shared rr_anchor grammar) ───────────────────

def _anchor_for(steps: list[tuple[str, int]], bookmark: str | None) -> dict[str, str]:
    """A stable OOXML node identity: a `bookmark(NAME)` path when a bookmark governs the node, else
    an absolute `body`-rooted body-walk path. Both are `kind:"ooxml_path"`. Built via the shared
    rr_anchor grammar so a consumer resolves EXACTLY what infer-office emits."""
    if bookmark is not None:
        return {"kind": "ooxml_path", "value": rr_anchor.ooxml_bookmark_value(bookmark)}
    return {"kind": "ooxml_path", "value": rr_anchor.ooxml_path_value(steps)}


def _child_governance(children: list[ET.Element]) -> dict[int, str]:
    """Map child-index -> governing bookmark name: a named w:bookmarkStart governs the element at
    the very next index (the shared bookmark rule in rr_anchor). First bookmark wins."""
    gov: dict[int, str] = {}
    for i, ch in enumerate(children):
        if _local(ch.tag) == "bookmarkStart":
            name = _bookmark_name(ch)
            if name is not None and i + 1 < len(children):
                gov.setdefault(i + 1, name)
    return gov


def _walk(
    el: ET.Element,
    steps: list[tuple[str, int]],
    bookmark: str | None,
    ctx: dict[str, Any],
    threshold: float,
    template_id: str,
    seen_ids: dict[str, int],
    period_holder: list[str | None],
    stats: dict[str, Any],
) -> dict[str, Any]:
    local = _local(el.tag)

    # data-shaped-literal detection (REUSED verbatim from the HTML lane) — runs on a run's OWN
    # direct w:t text; containers hold none, so a value is flagged exactly once (at its run).
    own_text = _run_own_text(el) if local == "r" else ""
    shaped_info = infer.detect_data_shaped_literal(own_text)
    shaped = bool(shaped_info["is_data_shaped"])

    # period detection + propagation (nearest governing reporting-period label, document order).
    is_period = False
    if local == "r" and own_text:
        pm = _PERIOD_RE.search(own_text)
        if pm is not None:
            is_period = True
            period_holder[0] = pm.group(0)
    current_period = period_holder[0]

    drawing_is_chart = ctx.get("drawing_is_chart", False)
    if local == "drawing":
        drawing_is_chart = _drawing_is_chart(el)
    local_ctx = dict(ctx)
    local_ctx["drawing_is_chart"] = drawing_is_chart

    role = _infer_role(local, local_ctx, shaped, is_period)
    cls, confidence, method = _classify(local, shaped, bookmark is not None, threshold)
    provenance = _provenance(local, shaped, is_period, current_period, method, template_id)

    anchor = _anchor_for(steps, bookmark)
    node_id = anchor["value"]
    if node_id in seen_ids:
        seen_ids[node_id] += 1
        node_id = f"{node_id}#{seen_ids[node_id]}"
    else:
        seen_ids[node_id] = 0

    # accounting
    stats["classes"][cls] = stats["classes"].get(cls, 0) + 1
    stats["roles"][role] = stats["roles"].get(role, 0) + 1
    if shaped:
        stats["data_shaped"] += 1
    if cls == "needs-review":
        stats["needs_review"] += 1
    if bookmark is not None and bookmark not in stats["bookmarks"]:
        stats["bookmarks"].append(bookmark)

    # descend into WALKED children only; a w:drawing is a leaf (not descended into).
    child_nodes: list[dict[str, Any]] = []
    if local != "drawing":
        # context inherited by children
        child_ctx = dict(ctx)
        if local == "p":
            style = _paragraph_style(el)
            child_ctx["heading_style"] = style in _HEADING_STYLES if style else False
        if local == "tc":
            child_ctx["in_tc"] = True

        raw_children = list(el)
        child_qnames = [c.tag for c in raw_children]
        governance = _child_governance(raw_children)
        for i, child in enumerate(raw_children):
            cl = _local(child.tag)
            if cl not in _WALK_LOCALS:
                continue
            idx = rr_anchor.ooxml_sibling_index(child_qnames, i)
            child_steps = steps + [(cl, idx)]
            child_bookmark = governance.get(i)
            child_nodes.append(
                _walk(
                    child,
                    child_steps,
                    child_bookmark,
                    child_ctx,
                    threshold,
                    template_id,
                    seen_ids,
                    period_holder,
                    stats,
                )
            )

    return {
        "id": node_id,
        "anchor": anchor,
        "role": role,
        "class": cls,
        "confidence": round(confidence, 3),
        "provenance": provenance,
        "data_shaped_literal": shaped,
        "children": child_nodes,
    }


def _reject_dtd(document_xml: bytes) -> None:
    """XXE / billion-laughs defense (stdlib-only floor — defusedxml is not on this plugin's
    dependency path). A valid OOXML word/document.xml NEVER carries a DTD, so a DOCTYPE/ENTITY
    declaration can only be a hostile template attempting external-entity (XXE) or internal
    entity-expansion abuse. Reject it before xml.etree ever expands anything. (A literal `<!DOCTYPE`
    can never appear in valid XML text content — it would be entity-escaped — so this has no false
    positives.) Mirrors the expat-level rejection in scripts/rr_anchor.py."""
    low = document_xml.lower()
    if b"<!doctype" in low or b"<!entity" in low:
        raise OfficeInferError(
            "DOCTYPE/DTD/ENTITY in word/document.xml is rejected (XXE / entity-expansion defense)"
        )


def build_rsg(
    document_xml: bytes,
    template_id: str,
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Parse `word/document.xml` bytes into an RSG dict + a stats dict. Pure (no I/O)."""
    _reject_dtd(document_xml)
    try:
        root = ET.fromstring(document_xml)
    except ET.ParseError as exc:
        raise OfficeInferError(f"word/document.xml is not well-formed XML: {exc}")
    body = None
    for node in root.iter():
        if _local(node.tag) == "body":
            body = node
            break
    if body is None:
        raise OfficeInferError("word/document.xml has no w:body element")

    stats: dict[str, Any] = {
        "classes": {},
        "roles": {},
        "data_shaped": 0,
        "needs_review": 0,
        "bookmarks": [],
        "total_nodes": 0,
        "accelerator": _ACCEL,
    }
    root_node = _walk(
        body,
        [],  # body-relative steps (body itself is the root -> "body")
        None,
        {"heading_style": False, "in_tc": False, "drawing_is_chart": False},
        threshold,
        template_id,
        {},
        [None],
        stats,
    )
    stats["total_nodes"] = sum(stats["classes"].values())
    rsg = {
        "schema_version": RSG_SCHEMA_VERSION,
        "format": "office",
        "template_id": template_id,
        "root": root_node,
    }
    return rsg, stats


# ── CLI (mirrors infer.py's surface + exit-code contract) ─────────────────────────────────────

def _summary(rsg: dict[str, Any], stats: dict[str, Any], in_path: str, out_path: str) -> dict[str, Any]:
    return {
        "ok": True,
        "in": in_path,
        "out": out_path,
        "template_id": rsg["template_id"],
        "format": rsg["format"],
        "schema_version": rsg["schema_version"],
        "total_nodes": stats["total_nodes"],
        "classes": stats["classes"],
        "roles": stats["roles"],
        "data_shaped_nodes": stats["data_shaped"],
        "needs_review_nodes": stats["needs_review"],
        "bookmarks_found": sorted(stats["bookmarks"]),
        "accelerator": stats["accelerator"] or "stdlib(zipfile+xml.etree)",
    }


def _emit_error(message: str, as_json: bool) -> int:
    print(f"[infer-office] error: {message}", file=sys.stderr)
    if as_json:
        print(json.dumps({"ok": False, "error": message}))
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="infer_office.py",
        description="Infer a Report Structure Graph (RSG) from a Word (.docx) report template.",
    )
    parser.add_argument("--in", dest="in_path", required=True, help="input .docx template (relative or in-repo)")
    parser.add_argument("--out", dest="out_path", required=True, help="output RSG JSON path (relative or in-repo)")
    parser.add_argument("--template-id", dest="template_id", default=None, help="stable template identity (default: input filename stem)")
    parser.add_argument("--confidence-threshold", dest="threshold", type=float, default=DEFAULT_CONFIDENCE_THRESHOLD, help="sub-threshold confidence -> needs-review (default %(default)s)")
    parser.add_argument("--format", dest="fmt", choices=["text", "json"], default="text", help="stdout summary format")
    args = parser.parse_args(argv)
    as_json = args.fmt == "json"

    try:
        in_abs = infer._safe_path(args.in_path, must_exist=True)
        out_abs = infer._safe_path(args.out_path, must_exist=False)
    except infer.InferError as exc:
        return _emit_error(str(exc), as_json)

    try:
        document_xml = read_document_xml(in_abs)
    except OfficeInferError as exc:
        return _emit_error(str(exc), as_json)
    except OSError as exc:
        return _emit_error(f"cannot read input: {exc}", as_json)

    template_id = args.template_id or os.path.splitext(os.path.basename(in_abs))[0]

    try:
        rsg, stats = build_rsg(document_xml, template_id, args.threshold)
    except infer.InferError as exc:
        return _emit_error(str(exc), as_json)
    except Exception as exc:  # never a silent crash-as-success
        return _emit_error(f"parse/build failed: {exc}", as_json)

    # Code to the SCHEMA: validate before writing (reusing the HTML lane's validator).
    try:
        schema = infer.load_schema()
    except Exception as exc:
        return _emit_error(f"cannot load rsg.schema.json: {exc}", as_json)
    schema_errors = infer.validate_instance(rsg, schema)
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
        print("[infer-office] OK — {} nodes -> {}".format(summary["total_nodes"], args.out_path))
        print("  template_id: {}   format: {}   parser: {}".format(
            summary["template_id"], summary["format"], summary["accelerator"]))
        print("  classes: {}".format(summary["classes"]))
        print("  roles: {}".format(summary["roles"]))
        print("  data-shaped nodes: {}   needs-review nodes: {}".format(
            summary["data_shaped_nodes"], summary["needs_review_nodes"]))
        print("  bookmarks found ({}): {}".format(
            len(summary["bookmarks_found"]), ", ".join(summary["bookmarks_found"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
