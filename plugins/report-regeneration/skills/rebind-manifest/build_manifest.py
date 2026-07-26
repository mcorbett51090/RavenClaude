#!/usr/bin/env python3
"""
build_manifest.py — report-regeneration pipeline stage 2 (detect -> strip -> rebind).

Turns a Report Structure Graph (RSG) plus the OLD template plus the NEW dataset into a
schema-valid Binding Manifest (binding-manifest.schema.json) and a taint dictionary
(the V4 egress leg's OLD-report literal inventory). This is the "surgeon planning the
transplant" stage: it does NOT render, it addresses + classifies + proposes queries.

Usage:
    python3 build_manifest.py \
        --rsg <rsg.json> --template <template.html> --new-data <data.json> \
        --out <manifest.json> [--taint-out <taint-dict.json>] \
        [--manifest-version 0.1.0] [--confidence-threshold 0.7] \
        [--format json|text] [--pretty]

Exit codes:
    0 — success: manifest built AND validated against binding-manifest.schema.json
    2 — usage / path-guard / parse error / input RSG failed rsg.schema.json (fail-closed)
    3 — manifest was built but FAILED binding-manifest.schema.json validation (a builder bug;
        the invalid output is still written so it can be inspected, but the exit is non-zero)

What it does, in order (mirrors core-architecture-spec.md sec.3/sec.4/sec.6):
    1. Build the TAINT DICTIONARY from the OLD template — distinct rendered value literals
       (via the pinned, non-inference data-shaped-literal detector) plus identity strings
       (author / company / title / source-filename), including a declared prior-artifact
       taint block (`old_company: "..."` comment convention) when present. This is the V4
       leg's dictionary of the old report's data.
    2. Apply the EARNED-`frozen` rule. `frozen` is never the default. A node proposed
       `frozen` is demoted to `needs-review` if an INDEPENDENT re-run of the data-shaped
       detector over its rendered text fires (or the RSG already flagged it), OR its text
       carries an old-taint value, OR it carries a new-dataset value. A data-shaped literal
       force-demotes regardless of classifier confidence (guarantee #2).
    3. Force RASTER / embedded-data-cache nodes to `regenerate` (a transplanted binary blob
       cannot be proven data-free — construction rule, overrides everything).
    4. Propose one binding per NON-static RSG node: node_id, anchor, class, confidence,
       provenance {source, source_period, method, pbi_route}, data_query. A `frozen` binding
       carries NO data_query; every non-frozen class MUST carry one.
    5. Validate the manifest against binding-manifest.schema.json (a small, stdlib-only JSON
       Schema validator — no pip).

Format support:
    - HTML template (default): the taint dictionary is built from the rendered HTML text +
      identity strings via the html.parser path (unchanged, byte-identical to prior behavior).
    - Office (`.docx`) template: the template is an OPC/ZIP (not UTF-8 text), so it is format-
      detected by extension/magic (`PK` zip => office) and the taint dictionary is built from the
      DECODED container — word/document.xml story text (data-shaped literals), the docProps
      identity strings (Author / lastModifiedBy / Title / Company), and any word/embeddings/*.xlsx
      cell values (the embedded chart-data cache = the client's old dataset). The RSG walk / earned-
      frozen / raster-force / query-proposal logic is format-neutral (office anchors are
      `ooxml_path`, never element-indexed), so only template ingestion + taint differ per format.

Design constraints (binding, per the plugin constitution):
    - Stdlib only (argparse / html.parser / re / json / pathlib / sys, plus zipfile / io /
      xml.etree for the docx decoded-container read). No third-party imports, no pip, no network,
      no subprocess. Runs on Python 3.9.6.
    - `from __future__ import annotations`; no `X | Y` runtime types, no match statement.
    - Path-guarded: input/output paths reject `..` traversal; resolution is deterministic. Every
      OOXML part is parsed DTD/XXE-safe (a DOCTYPE/ENTITY in a part is refused before expansion).
"""
from __future__ import annotations

import argparse
import html.parser
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

SCHEMA_TAG = "report-regeneration/rebind-manifest@1"
TAINT_SCHEMA_TAG = "report-regeneration/taint-dict@1"

# ── knowledge-dir schemas (single source of truth; loaded, never re-declared here) ──

_KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent.parent / "knowledge"
_MANIFEST_SCHEMA_PATH = _KNOWLEDGE_DIR / "binding-manifest.schema.json"
_RSG_SCHEMA_PATH = _KNOWLEDGE_DIR / "rsg.schema.json"


class BuildManifestError(Exception):
    """Raised for path-guard / parse / usage failures (exit 2)."""


# ── path safety (mirrors scripts/seed_defects.py's guard, but usable with absolute user paths) ──

def _guard_path(raw: str, *, must_exist: bool) -> Path:
    """Resolve `raw` deterministically and reject `..` traversal. Absolute user paths are
    allowed (this is a user-facing CLI, not a repo-internal fixture tool), but traversal
    components are never accepted. Never opens a network resource."""
    if not raw:
        raise BuildManifestError("empty path")
    p = Path(raw)
    if ".." in p.parts:
        raise BuildManifestError(f"path traversal ('..') is not allowed: {raw!r}")
    resolved = p if p.is_absolute() else (Path.cwd() / p)
    resolved = resolved.resolve()
    if must_exist and not resolved.is_file():
        raise BuildManifestError(f"input file not found: {raw!r} (resolved {resolved})")
    return resolved


# ── the pinned, non-inference data-shaped-literal detector (currency/percent/date/number/unit) ──
# Deliberately dumb: it fires on "100%" in a marketing tagline exactly as on a KPI's "100%".
# That over-flagging is the SAFE direction (guarantee #2: surface for review); under-flagging
# a data-bound frozen node is what a leak looks like.

_DETECTORS = [
    ("currency", re.compile(r"[$€£¥]\s?\d{1,3}(?:,\d{3})*(?:\.\d+)?")),
    ("currency_word", re.compile(r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s?(?:USD|EUR|GBP|dollars?)\b", re.I)),
    ("percent", re.compile(r"[-+]?\d+(?:\.\d+)?\s?%")),
    ("date_month", re.compile(
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b", re.I)),
    ("date_iso", re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),
    ("date_num", re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")),
    ("quarter", re.compile(r"\bQ[1-4]\s?\d{4}\b|\b\d{4}[-/]Q[1-4]\b", re.I)),
    ("grouped_num", re.compile(r"[-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?")),
    ("decimal", re.compile(r"[-+]?\d+\.\d+")),
    ("unit_num", re.compile(r"\b\d+(?:\.\d+)?\s?(?:M|K|B|bn|m|k)\b")),
]


def find_data_shaped(text: str) -> list:
    """Return the distinct data-shaped literals found in `text` (in first-seen order)."""
    if not text:
        return []
    seen = []
    seen_set = set()
    for _kind, pat in _DETECTORS:
        for m in pat.findall(text):
            token = m if isinstance(m, str) else m[0]
            token = token.strip()
            if token and token not in seen_set:
                seen_set.add(token)
                seen.append(token)
    return seen


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


# ── template parsing (stdlib html.parser; builds id->element + visible text + comments) ──

_VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


class _TemplateParser(html.parser.HTMLParser):
    """Collect: id -> {tag, attrs, text}; visible text; script bodies; comments; <title>;
    <h1>s; <meta> attrs. Inner text of an id'd element is every text node between its start
    and end tag (including nested)."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack = []          # open non-void elements: {"tag","attrs","id","buf"}
        self.elements = {}       # id -> {"tag","attrs","text"}
        self.visible = []        # text outside <style>/<script>
        self.scripts = []        # <script> bodies (embedded-cache channel)
        self.comments = []       # raw comment strings
        self.metas = []          # list of attr dicts for <meta>
        self.title_parts = []
        self.h1_texts = []
        self._style_depth = 0
        self._script_depth = 0
        self._title_depth = 0
        self._h1_depth = 0
        self._cur_h1 = []

    # -- helpers --
    def _attrs_dict(self, attrs) -> dict:
        return {(k or "").lower(): (v if v is not None else "") for k, v in attrs}

    def _record_void(self, tag: str, attrs_d: dict) -> None:
        if tag == "meta":
            self.metas.append(attrs_d)
        elem_id = attrs_d.get("id")
        if elem_id:
            self.elements[elem_id] = {"tag": tag, "attrs": attrs_d, "text": ""}

    # -- events --
    def handle_starttag(self, tag, attrs):
        attrs_d = self._attrs_dict(attrs)
        if tag in _VOID_TAGS:
            self._record_void(tag, attrs_d)
            return
        if tag == "style":
            self._style_depth += 1
        elif tag == "script":
            self._script_depth += 1
        elif tag == "title":
            self._title_depth += 1
        elif tag == "h1":
            self._h1_depth += 1
            if self._h1_depth == 1:
                self._cur_h1 = []
        self.stack.append({"tag": tag, "attrs": attrs_d, "id": attrs_d.get("id"), "buf": []})

    def handle_startendtag(self, tag, attrs):
        self._record_void(tag, self._attrs_dict(attrs))

    def handle_data(self, data):
        for entry in self.stack:
            if entry["id"] is not None:
                entry["buf"].append(data)
        if self._style_depth == 0 and self._script_depth == 0:
            self.visible.append(data)
        if self._script_depth > 0:
            self.scripts.append(data)
        if self._title_depth > 0:
            self.title_parts.append(data)
        if self._h1_depth > 0:
            self._cur_h1.append(data)

    def handle_endtag(self, tag):
        idx = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]["tag"] == tag:
                idx = i
                break
        if idx is None:
            return
        # pop everything from idx up (handles minor malformation), recording id'd elements
        while len(self.stack) > idx:
            entry = self.stack.pop()
            if entry["id"]:
                self.elements.setdefault(entry["id"], {
                    "tag": entry["tag"], "attrs": entry["attrs"],
                    "text": "".join(entry["buf"]),
                })
                # prefer the fully-closed text
                self.elements[entry["id"]] = {
                    "tag": entry["tag"], "attrs": entry["attrs"],
                    "text": "".join(entry["buf"]),
                }
        if tag == "style" and self._style_depth > 0:
            self._style_depth -= 1
        elif tag == "script" and self._script_depth > 0:
            self._script_depth -= 1
        elif tag == "title" and self._title_depth > 0:
            self._title_depth -= 1
        elif tag == "h1" and self._h1_depth > 0:
            self._h1_depth -= 1
            if self._h1_depth == 0:
                self.h1_texts.append("".join(self._cur_h1))

    def handle_comment(self, data):
        self.comments.append(data)

    def finalize(self) -> None:
        # flush any unclosed id'd elements (best-effort; well-formed fixtures leave none)
        while self.stack:
            entry = self.stack.pop()
            if entry["id"] and entry["id"] not in self.elements:
                self.elements[entry["id"]] = {
                    "tag": entry["tag"], "attrs": entry["attrs"],
                    "text": "".join(entry["buf"]),
                }


def parse_template(path) -> dict:
    text = Path(path).read_text(encoding="utf-8")
    parser = _TemplateParser()
    parser.feed(text)
    parser.close()
    parser.finalize()
    return {
        "elements": parser.elements,
        "visible": "".join(parser.visible),
        "scripts": parser.scripts,
        "comments": parser.comments,
        "title": "".join(parser.title_parts).strip(),
        "h1": [t.strip() for t in parser.h1_texts if t.strip()],
        "metas": parser.metas,
    }


# ── taint dictionary — the V4 leg's inventory of the OLD report's data (sec.6 step 1) ──

# Keys we accept from a declared prior-artifact taint block embedded as an HTML comment
# (the `old_company: "..."` convention used by the Phase-0 corpus). This captures literals
# from the PRIOR client artifact that "do not appear in the rendered body by default".
_TAINT_KEY = re.compile(
    r'^\s*(old_[a-z_]+|author|company|title|source_file|source_filename)\s*:\s*"([^"]+)"\s*$',
    re.M,
)
_IDENTITY_KEYS = {
    "old_company", "old_author", "old_source_file",
    "author", "company", "title", "source_file", "source_filename",
}


def build_taint_dictionary(template_path) -> dict:
    """Build the taint dictionary from the OLD template: distinct rendered value literals +
    identity strings (author/company/title/source-filename), plus any declared prior-artifact
    taint block. Returns a serializable dict with `values`, `identity_strings`, and the union
    `all` (originals) that the V4 egress leg and the earned-frozen rule scan against."""
    info = parse_template(template_path)

    values = []
    values_set = set()

    def add_value(v: str) -> None:
        v = v.strip()
        if v and v not in values_set:
            values_set.add(v)
            values.append(v)

    for token in find_data_shaped(info["visible"]):
        add_value(token)
    for body in info["scripts"]:
        for token in find_data_shaped(body):
            add_value(token)

    identity = []
    identity_set = set()

    def add_identity(v: str) -> None:
        v = v.strip()
        if v and v not in identity_set:
            identity_set.add(v)
            identity.append(v)

    if info["title"]:
        add_identity(info["title"])
    for h in info["h1"]:
        add_identity(h)
    for meta in info["metas"]:
        name = meta.get("name", "").lower()
        content = meta.get("content", "")
        if content and name in {"author", "company", "generator", "dc.creator", "dcterms.creator"}:
            add_identity(content)

    # declared prior-artifact taint block(s)
    for comment in info["comments"]:
        for key, val in _TAINT_KEY.findall(comment):
            if key in _IDENTITY_KEYS:
                add_identity(val)
            else:
                add_value(val)

    union = []
    union_set = set()
    for v in identity + values:
        if v not in union_set:
            union_set.add(v)
            union.append(v)

    return {
        "schema": TAINT_SCHEMA_TAG,
        "template": str(template_path),
        "values": sorted(values),
        "identity_strings": sorted(identity),
        "all": sorted(union),
    }


# ── Office (docx) decoded-container taint — the OOXML analogue of build_taint_dictionary ──────
# Mirrors the fidelity harness's decoded-container logic (report-fidelity-harness/harness.py
# `_decoded_container_office` / `derive_taint_office`) with a small self-contained stdlib helper
# (zipfile + xml.etree), so build_manifest stays dependency-free. A .docx is an OPC/ZIP, never
# UTF-8 text, so the HTML `read_text` path would raise UnicodeDecodeError on it — this is the
# format-detected branch that build_taint_dictionary_office serves.

_OFFICE_EMBEDDINGS_PREFIX = "word/embeddings/"
_RE_RAW_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")


def _reject_dtd_bytes(data: bytes) -> None:
    """XXE / billion-laughs defense (stdlib floor; mirrors harness/rr_anchor). A valid OOXML part
    NEVER carries a DTD, so any DOCTYPE/ENTITY is a hostile template refused before xml.etree
    expands anything."""
    low = data.lower()
    if b"<!doctype" in low or b"<!entity" in low:
        raise BuildManifestError(
            "DOCTYPE/DTD/ENTITY in an OOXML part is rejected (XXE / entity-expansion defense)"
        )


def _read_docx_parts(template_path, max_parts: int = 8000) -> dict:
    """Decode the .docx OPC package into {part_name: raw_bytes}. Path already resolved by the
    caller; this is a byte read + in-memory unzip (no second path read, no network)."""
    raw = Path(template_path).read_bytes()
    if raw[:2] != b"PK":
        raise BuildManifestError(f"{template_path}: not an OPC/zip (.docx) container")
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
        raise BuildManifestError(f"{template_path}: corrupt .docx zip: {exc}")
    if "word/document.xml" not in parts:
        raise BuildManifestError(f"{template_path}: no word/document.xml part (not a Word .docx?)")
    return parts


def _local_name(tag) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _xml_all_text(data: bytes) -> str:
    """All element text + tails of an XML part (the story/identity text surface). A not-well-formed
    part falls back to the raw decoded bytes so a literal is never missed."""
    if not data:
        return ""
    _reject_dtd_bytes(data)
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return data.decode("utf-8", "replace")
    out: list = []
    for el in root.iter():
        if el.text:
            out.append(el.text)
        if el.tail:
            out.append(el.tail)
    return " ".join(out)


def _xml_first_local_text(data: bytes, local: str):
    """The text of the FIRST element whose local name is `local` (namespace-agnostic)."""
    if not data:
        return None
    _reject_dtd_bytes(data)
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return None
    for el in root.iter():
        if _local_name(el.tag) == local and el.text and el.text.strip():
            return el.text.strip()
    return None


def _xlsx_cell_values(data: bytes) -> list:
    """The value inventory of an embedded chart-data cache (a nested .xlsx OPC zip): every `<v>`
    (cell value) and `<t>` (shared/inline string) token, plus any data-shaped literal in its XML.
    An embedded cache stores figures RAW (e.g. `9876543`, no `$`/commas), which the data-shaped
    detector alone would miss — so bare `<v>` numerics are captured explicitly."""
    tokens: list = []
    if data[:2] != b"PK":
        return tokens
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                if not name.lower().endswith(".xml"):
                    continue
                part = zf.read(name)
                try:
                    _reject_dtd_bytes(part)
                    root = ET.fromstring(part)
                except (ET.ParseError, BuildManifestError):
                    tokens.extend(find_data_shaped(part.decode("utf-8", "replace")))
                    continue
                for el in root.iter():
                    if _local_name(el.tag) in ("v", "t") and el.text and el.text.strip():
                        tokens.append(el.text.strip())
                tokens.extend(find_data_shaped(_xml_all_text(part)))
    except zipfile.BadZipFile:
        pass
    return tokens


def build_taint_dictionary_office(template_path) -> dict:
    """Office analogue of build_taint_dictionary: build the taint dictionary from the DECODED docx
    container. Same serialized shape (`values` / `identity_strings` / `all`) the V4 egress leg and
    the earned-frozen rule scan against. Sources: word/document.xml story text (data-shaped
    literals), docProps identity strings (Author / lastModifiedBy / Title / Company), and any
    word/embeddings/*.xlsx cell values (the client's old dataset cache)."""
    parts = _read_docx_parts(template_path)

    values: list = []
    values_set: set = set()

    def add_value(v: str) -> None:
        v = (v or "").strip()
        if v and v not in values_set:
            values_set.add(v)
            values.append(v)

    identity: list = []
    identity_set: set = set()

    def add_identity(v) -> None:
        v = (v or "").strip() if v else ""
        if v and v not in identity_set:
            identity_set.add(v)
            identity.append(v)

    # (1) document.xml story text — the rendered data-shaped literals
    for token in find_data_shaped(_xml_all_text(parts.get("word/document.xml", b""))):
        add_value(token)

    # (2) docProps identity strings (a direct identity-leak surface)
    core = parts.get("docProps/core.xml", b"")
    for local in ("creator", "lastModifiedBy", "title"):
        add_identity(_xml_first_local_text(core, local))
    add_identity(_xml_first_local_text(parts.get("docProps/app.xml", b""), "Company"))

    # (3) embedded chart-data cache values (word/embeddings/*.xlsx) — the old dataset
    for name, data in parts.items():
        low = name.lower()
        if name.startswith(_OFFICE_EMBEDDINGS_PREFIX) and low.endswith((".xlsx", ".xlsm")):
            for token in _xlsx_cell_values(data):
                add_value(token)

    union: list = []
    union_set: set = set()
    for v in identity + values:
        if v not in union_set:
            union_set.add(v)
            union.append(v)

    return {
        "schema": TAINT_SCHEMA_TAG,
        "template": str(template_path),
        "values": sorted(values),
        "identity_strings": sorted(identity),
        "all": sorted(union),
    }


def _detect_template_format(template_path) -> str:
    """html vs office, by extension then magic (`PK` zip => office). Deterministic, path already
    resolved by the caller."""
    p = Path(template_path)
    ext = p.suffix.lower()
    if ext in (".docx", ".docm"):
        return "office"
    if ext in (".html", ".htm", ".xhtml"):
        return "html"
    try:
        with open(p, "rb") as fh:
            head = fh.read(4)
    except OSError:
        return "html"
    return "office" if head[:2] == b"PK" else "html"


# ── new dataset — the new value domains the earned-frozen rule tests against ──

_RESERVED_NEWDATA_KEYS = {"source_ref", "dataset_id", "source", "source_period", "values"}


def _collect_scalars(obj, out: set) -> None:
    if isinstance(obj, dict):
        for v in obj.values():
            _collect_scalars(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect_scalars(v, out)
    elif isinstance(obj, bool):
        return
    elif isinstance(obj, (str, int, float)):
        out.add(str(obj))


def load_new_data(path) -> dict:
    """Load the new dataset. Recognized shape:
        {"source_ref": "...", "source_period": "...", "values": [...] | {...}}
    `values` (list or dict) is the explicit new value domain; if absent, every scalar leaf
    (except the reserved metadata keys) is treated as a domain value."""
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise BuildManifestError("--new-data must be a JSON object")
    source_ref = (
        doc.get("source_ref") or doc.get("dataset_id") or doc.get("source") or Path(path).name
    )
    source_period = doc.get("source_period")
    domain = set()
    raw = doc.get("values")
    if raw is None:
        raw = {k: v for k, v in doc.items() if k not in _RESERVED_NEWDATA_KEYS}
    _collect_scalars(raw, domain)
    return {
        "source_ref": str(source_ref),
        "source_period": source_period,
        "value_domain": sorted(domain),
    }


# ── minimal, stdlib-only JSON Schema validator (subset used by our two schemas) ──
# Supports: $ref (local #/...), type (str or list), enum, const, required, properties,
# additionalProperties (bool|schema), items, pattern, minLength, minimum, maximum, allOf,
# anyOf, not, if/then/else. Enough to "code to the SCHEMAS" without pip.

def _resolve_ref(ref: str, root: dict):
    if not ref.startswith("#/"):
        raise BuildManifestError(f"unsupported $ref (only local pointers): {ref!r}")
    node = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        node = node[part]
    return node


def _type_ok(instance, type_name: str) -> bool:
    if type_name == "object":
        return isinstance(instance, dict)
    if type_name == "array":
        return isinstance(instance, list)
    if type_name == "string":
        return isinstance(instance, str)
    if type_name == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if type_name == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if type_name == "boolean":
        return isinstance(instance, bool)
    if type_name == "null":
        return instance is None
    return True


def validate(instance, schema, root, path: str = "$") -> list:
    """Return a list of human-readable error strings ([] == valid)."""
    errs = []
    if isinstance(schema, bool):
        if schema is False:
            errs.append(f"{path}: schema is false (nothing is valid here)")
        return errs
    if "$ref" in schema:
        return validate(instance, _resolve_ref(schema["$ref"], root), root, path)

    if "type" in schema:
        t = schema["type"]
        types = t if isinstance(t, list) else [t]
        if not any(_type_ok(instance, tt) for tt in types):
            errs.append(f"{path}: expected type {t}, got {type(instance).__name__}")
    if "enum" in schema and instance not in schema["enum"]:
        errs.append(f"{path}: {instance!r} not in enum {schema['enum']}")
    if "const" in schema and instance != schema["const"]:
        errs.append(f"{path}: {instance!r} != const {schema['const']!r}")

    if isinstance(instance, str):
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errs.append(f"{path}: {instance!r} does not match pattern {schema['pattern']!r}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errs.append(f"{path}: length {len(instance)} < minLength {schema['minLength']}")
    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errs.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errs.append(f"{path}: {instance} > maximum {schema['maximum']}")

    if isinstance(instance, dict):
        props = schema.get("properties", {})
        for req in schema.get("required", []):
            if req not in instance:
                errs.append(f"{path}: missing required property {req!r}")
        addl = schema.get("additionalProperties", True)
        for key, val in instance.items():
            if key in props:
                errs += validate(val, props[key], root, f"{path}.{key}")
            elif isinstance(addl, dict):
                errs += validate(val, addl, root, f"{path}.{key}")
            elif addl is False:
                errs.append(f"{path}: additional property {key!r} not allowed")
    if isinstance(instance, list):
        items = schema.get("items")
        if isinstance(items, dict):
            for i, item in enumerate(instance):
                errs += validate(item, items, root, f"{path}[{i}]")

    for sub in schema.get("allOf", []):
        errs += validate(instance, sub, root, path)
    if "anyOf" in schema and not any(
        not validate(instance, sub, root, path) for sub in schema["anyOf"]
    ):
        errs.append(f"{path}: does not match anyOf")
    if "not" in schema and not validate(instance, schema["not"], root, path):
        errs.append(f"{path}: must NOT match subschema (not)")
    if "if" in schema:
        if not validate(instance, schema["if"], root, path):
            if "then" in schema:
                errs += validate(instance, schema["then"], root, path)
        elif "else" in schema:
            errs += validate(instance, schema["else"], root, path)
    return errs


def _load_schema(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(manifest: dict) -> list:
    schema = _load_schema(_MANIFEST_SCHEMA_PATH)
    return validate(manifest, schema, schema)


def validate_rsg(rsg: dict) -> list:
    schema = _load_schema(_RSG_SCHEMA_PATH)
    return validate(rsg, schema, schema)


# ── the rebind decision — earned-frozen + raster-force + query proposal (sec.4) ──

_RASTER_ROLES = {"image", "chart"}


def _detect_raster(tag, attrs: dict, role: str, pbi_route) -> bool:
    """A node that renders as a raster or carries an embedded binary/data cache MUST be
    `regenerate` (a transplanted blob cannot be proven data-free)."""
    if role in _RASTER_ROLES:
        return True
    if pbi_route == "screenshot":
        return True
    if tag == "img":
        return True
    if attrs.get("src", "").startswith("data:"):
        return True
    if tag == "script" and "json" in attrs.get("type", "").lower():
        return True
    return False


def _contains_domain_value(text_norm: str, domain_norm) -> str:
    for value in domain_norm:
        if len(value) >= 2 and value in text_norm:
            return value
    return ""


def propose_query(final_class: str, role: str, pbi_route, bind_key: str, source_ref: str):
    """Propose a data_query. `frozen` -> None (carries no data). Every non-frozen class MUST
    carry a query object {kind, expression[, source_ref]}."""
    if final_class == "frozen":
        return None
    if final_class == "needs-review":
        return {
            "kind": "none",
            "expression": "pending human sign-off; no binding proposed until reviewed",
        }
    if pbi_route in ("xmla", "rest"):
        expr = (f'EVALUATE ROW("{bind_key}", [{bind_key}])' if bind_key
                else 'EVALUATE ROW("value", [Measure])')
        query = {"kind": "dax", "expression": expr}
    elif pbi_route == "screenshot" or role in _RASTER_ROLES:
        query = {"kind": "screenshot-capture",
                 "expression": "fresh capture/render from the new source (never transplanted)"}
    elif role in ("narrative", "heading"):
        query = {"kind": "literal-from-new-source",
                 "expression": bind_key or "regenerated from the new source"}
    else:  # kpi-value / table-cell / period-label / metadata / unknown
        query = {"kind": "file-cell", "expression": bind_key or "<new-data cell>"}
    if source_ref:
        query["source_ref"] = source_ref
    return query


def decide_binding(node: dict, template_index: dict, taint_norm, new_data: dict,
                   template_id: str, threshold: float) -> tuple:
    """Return (binding_dict, decision_dict). Enforces raster-force, earned-frozen demotion,
    and sub-threshold-confidence escalation; then proposes the query + provenance."""
    anchor = node["anchor"]
    role = node["role"]
    base = node["class"]
    conf = node["confidence"]
    prov = node.get("provenance", {})
    pbi_route = prov.get("pbi_route")

    element = template_index.get(anchor["value"]) if anchor.get("kind") == "element_id" else None
    rendered = element["text"] if element else ""
    tag = element["tag"] if element else None
    attrs = element["attrs"] if element else {}
    bind_key = attrs.get("data-bind", "")

    rendered_norm = _norm(rendered)
    detector_hits = find_data_shaped(rendered)
    ds_literal = bool(node.get("data_shaped_literal")) or bool(detector_hits)
    taint_hit = _contains_domain_value(rendered_norm, taint_norm)
    newdata_hit = _contains_domain_value(rendered_norm, new_data["_domain_norm"])
    is_raster = _detect_raster(tag, attrs, role, pbi_route)

    triggers = []
    if is_raster:
        final = "regenerate"
        reason = "raster/embedded-data-cache node -> forced regenerate (construction rule)"
        triggers.append("raster")
    elif base == "frozen":
        if ds_literal:
            final = "needs-review"
            reason = "data-shaped literal in a candidate-frozen node -> demote (hard rule)"
            triggers.append("data_shaped_literal")
        elif taint_hit:
            final = "needs-review"
            reason = f"old-taint value {taint_hit!r} in a candidate-frozen node -> cannot be frozen"
            triggers.append("old_taint_value")
        elif newdata_hit:
            final = "needs-review"
            reason = f"new-dataset value {newdata_hit!r} in a candidate-frozen node -> cannot be frozen"
            triggers.append("new_dataset_value")
        elif conf < threshold:
            final = "needs-review"
            reason = f"sub-threshold confidence {conf} < {threshold} -> surface for review"
            triggers.append("low_confidence")
        else:
            final = "frozen"
            reason = "earned frozen: no data-shaped literal, no taint value, no new-dataset value"
    else:
        if base == "surgical" and conf < threshold:
            final = "needs-review"
            reason = f"sub-threshold confidence {conf} < {threshold} -> surface for review"
            triggers.append("low_confidence")
        else:
            final = base
            reason = f"kept RSG-proposed class {base!r}"

    # provenance: frozen chrome traces to the template itself; everything else to the new source
    if final == "frozen":
        m_source = template_id or "template"
        m_period = None
    else:
        m_source = new_data["source_ref"]
        m_period = new_data.get("source_period") or prov.get("source_period")
    provenance = {"source": m_source, "source_period": m_period}
    if prov.get("method"):
        provenance["method"] = prov["method"]
    if prov.get("pbi_route") is not None:
        provenance["pbi_route"] = prov["pbi_route"]

    query = propose_query(final, role, pbi_route, bind_key, new_data["source_ref"])

    binding = {
        "node_id": node["id"],
        "anchor": {"kind": anchor["kind"], "value": anchor["value"]},
        "class": final,
        "confidence": conf,
        "provenance": provenance,
        "data_query": query,
    }
    decision = {
        "node_id": node["id"],
        "role": role,
        "proposed_class": base,
        "final_class": final,
        "reason": reason,
        "triggers": triggers,
        "detector_hits": detector_hits,
        "taint_hit": taint_hit or None,
        "newdata_hit": newdata_hit or None,
    }
    return binding, decision


def build_manifest(rsg: dict, template_index: dict, taint: dict, new_data: dict,
                   manifest_version: str, threshold: float) -> tuple:
    """Walk the RSG in document order (pre-order DFS), emit one binding per NON-static node."""
    taint_norm = [_norm(v) for v in taint["all"] if len(_norm(v)) >= 2]
    new_data = dict(new_data)
    new_data["_domain_norm"] = [_norm(v) for v in new_data["value_domain"]]
    template_id = rsg.get("template_id", "")

    bindings = []
    decisions = []

    def walk(node: dict) -> None:
        if node.get("role") != "static-chrome":
            binding, decision = decide_binding(
                node, template_index, taint_norm, new_data, template_id, threshold)
            bindings.append(binding)
            decisions.append(decision)
        for child in node.get("children", []):
            walk(child)

    walk(rsg["root"])

    manifest = {
        "manifest_version": manifest_version,
        "rsg_schema_version": rsg.get("schema_version", "0.0.0"),
        "template_id": template_id,
        "format": rsg.get("format", "html"),
        "bindings": bindings,
    }
    return manifest, decisions


# ── orchestration ──

def run(rsg_path, template_path, new_data_path, out_path, taint_out=None,
        manifest_version: str = "0.1.0", threshold: float = 0.7) -> dict:
    """End-to-end (paths already resolved). Writes the manifest + taint dict, returns a
    structured result. Raises BuildManifestError on RSG-schema-invalidity (fail-closed)."""
    rsg = json.loads(Path(rsg_path).read_text(encoding="utf-8"))
    rsg_errors = validate_rsg(rsg)
    if rsg_errors:
        raise BuildManifestError(
            "input RSG failed rsg.schema.json (fail-closed): " + "; ".join(rsg_errors[:8])
        )

    # Format-detect the template. HTML (default): rendered-text parse + taint (byte-identical to
    # prior behavior). Office (.docx): an OPC/ZIP, so ingest the DECODED container instead — the
    # element index is unused for office (its anchors are ooxml_path, never element-indexed), so an
    # empty index is correct, and the taint comes from the decoded-container builder.
    if _detect_template_format(template_path) == "office":
        template_info = {"elements": {}}
        taint = build_taint_dictionary_office(template_path)
    else:
        template_info = parse_template(template_path)
        taint = build_taint_dictionary(template_path)
    new_data = load_new_data(new_data_path)

    manifest, decisions = build_manifest(
        rsg, template_info["elements"], taint, new_data, manifest_version, threshold)
    manifest_errors = validate_manifest(manifest)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    taint_path = Path(taint_out) if taint_out else (out_path.parent / "taint-dict.json")
    taint_path.parent.mkdir(parents=True, exist_ok=True)
    taint_path.write_text(json.dumps(taint, indent=2) + "\n", encoding="utf-8")

    class_counts = {}
    for binding in manifest["bindings"]:
        class_counts[binding["class"]] = class_counts.get(binding["class"], 0) + 1

    return {
        "schema": SCHEMA_TAG,
        "ok": not manifest_errors,
        "manifest_path": str(out_path),
        "taint_dict_path": str(taint_path),
        "binding_count": len(manifest["bindings"]),
        "class_counts": class_counts,
        "taint_value_count": len(taint["values"]),
        "taint_identity_count": len(taint["identity_strings"]),
        "manifest_valid": not manifest_errors,
        "manifest_errors": manifest_errors,
        "decisions": decisions,
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="build_manifest.py",
        description="report-regeneration stage 2: turn an RSG + old template + new data into "
                    "a schema-valid Binding Manifest and a taint dictionary.",
    )
    p.add_argument("--rsg", required=True, metavar="PATH", help="input RSG JSON (rsg.schema.json)")
    p.add_argument("--template", required=True, metavar="PATH",
                   help="OLD template (HTML) — the surgical-transplant source")
    p.add_argument("--new-data", required=True, dest="new_data", metavar="PATH",
                   help="new dataset JSON (value domains for the earned-frozen rule)")
    p.add_argument("--out", required=True, metavar="PATH", help="output Binding Manifest JSON")
    p.add_argument("--taint-out", dest="taint_out", metavar="PATH",
                   help="taint-dict output path (default: taint-dict.json beside --out)")
    p.add_argument("--manifest-version", dest="manifest_version", default="0.1.0",
                   metavar="X.Y.Z", help="manifest_version to stamp (semver; default 0.1.0)")
    p.add_argument("--confidence-threshold", dest="threshold", type=float, default=0.7,
                   metavar="F", help="below this a classification is surfaced as needs-review")
    p.add_argument("--format", dest="fmt", choices=["json", "text"], default="json",
                   help="output format for the run summary on stdout (default json)")
    p.add_argument("--pretty", action="store_true",
                   help="pretty-print the JSON run summary")
    return p


def _emit_error(message: str) -> None:
    print(json.dumps({"schema": SCHEMA_TAG, "ok": False, "error": message}))
    print(f"[error] {message}", file=sys.stderr)


def main(argv) -> int:
    args = build_parser().parse_args(argv)

    if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", args.manifest_version):
        _emit_error(f"--manifest-version must be semver X.Y.Z, got {args.manifest_version!r}")
        return 2

    try:
        rsg_path = _guard_path(args.rsg, must_exist=True)
        template_path = _guard_path(args.template, must_exist=True)
        new_data_path = _guard_path(args.new_data, must_exist=True)
        out_path = _guard_path(args.out, must_exist=False)
        taint_out = _guard_path(args.taint_out, must_exist=False) if args.taint_out else None
    except BuildManifestError as exc:
        _emit_error(str(exc))
        return 2

    try:
        result = run(rsg_path, template_path, new_data_path, out_path, taint_out,
                     manifest_version=args.manifest_version, threshold=args.threshold)
    except BuildManifestError as exc:
        _emit_error(str(exc))
        return 2
    except (OSError, ValueError, KeyError) as exc:
        _emit_error(f"{type(exc).__name__}: {exc}")
        return 2

    if args.fmt == "text":
        print(f"manifest: {result['manifest_path']} ({result['binding_count']} bindings)")
        print(f"taint-dict: {result['taint_dict_path']} "
              f"({result['taint_value_count']} values, {result['taint_identity_count']} identity)")
        print(f"classes: {result['class_counts']}")
        print(f"valid: {result['manifest_valid']}")
        if result["manifest_errors"]:
            for err in result["manifest_errors"]:
                print(f"  ! {err}")
    else:
        print(json.dumps(result, indent=2 if args.pretty else None))

    return 0 if result["manifest_valid"] else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
