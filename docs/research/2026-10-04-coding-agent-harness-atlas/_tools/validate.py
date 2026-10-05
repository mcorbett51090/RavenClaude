"""Validate the harness-atlas data files and, optionally, the rendered HTML (plan P1).

Thirteen rules, each reported under its own rule name so a failure points at the rule:
R01 structure, R02 referential integrity, R03 state obligations, R04 markers, R05 evidence
quality, R06 install lines, R07 no numeric confidence, R08 levers, R09 task-shape rows,
R10 register, R11 completeness (--require-complete), R12 sizes, R13 HTML (--html-dir).

Enums, required keys, patterns and length limits are read from the schema files in
``schemas/`` at run time; this module keeps no copy of them. Only a small, fail-closed subset
of JSON Schema is implemented: a schema keyword outside that subset raises ``SchemaError``
instead of being silently ignored.

Usage: python3 validate.py [--data-dir DIR] [--require-complete] [--html-dir DIR] [--json]
                          [--no-repo-paths]
       python3 validate.py --selftest

``--no-repo-paths`` skips resolving task-row pointer files against the repository (a temporary
data directory has no repository to resolve them in).
Findings print one per line as ``<level> <rule> <where>: <message>``. Exit 0 only when there
is no ``error`` finding.
"""

import argparse
import base64
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import NamedTuple
from urllib.parse import urlsplit

from atlas_common import DATA_DIR, SCHEMA_DIR
from quotes import INSTALL_DESCRIPTION, install_text
from render import lever_key, ref_key

R_STRUCTURE = "R01-structure"
R_REFERENCE = "R02-referential-integrity"
R_STATE = "R03-state-obligation"
R_MARKER = "R04-marker"
R_EVIDENCE = "R05-evidence-quality"
R_INSTALL = "R06-install-line"
R_NUMERIC = "R07-numeric-confidence"
R_LEVER = "R08-lever"
R_TASK = "R09-task-shape"
R_REGISTER = "R10-register"
R_COMPLETE = "R11-completeness"
R_SIZE = "R12-size"
R_HTML = "R13-html"

# Decimal megabytes: the stricter reading of "MB", so a file that passes is under either.
MAX_DATA_FILE_BYTES = 2_000_000
MAX_HTML_PAGE_BYTES = 1_500_000
MAX_HTML_TOTAL_BYTES = 12_000_000

SCHEMA_NAMES = ("cell", "evidence", "lever", "register", "snapshot")
VERIFIED_TIERS = ("E1", "E2", "E3", "E4")
NUMERIC_KEYS = ("confidence", "probability", "certainty", "likelihood")
TASK_BASES = (
    "framework-rule",
    "capability-fact",
    "cost-heuristic",
    "editorial-judgment",
    "vendor-guidance",
)
TASK_ROW_KEYS = ("surface", "task_class", "pointer", "basis", "pending_label", "lever_settings")
POINTER_KEYS = ("file", "path")
POSITIVE_LOCATION_KINDS = ("vendor_managed", "not_applicable")
NEW_FILE_TYPES = ("extend", "new-lane")
MAX_PROPOSAL_WORDS = 120
EXTRA_HTML_HOSTS = ("github.com",)

_ANNOTATION_KEYS = {"$schema", "$id", "title", "description"}
_SUPPORTED_KEYWORDS = _ANNOTATION_KEYS | {
    "type",
    "enum",
    "required",
    "additionalProperties",
    "properties",
    "pattern",
    "maxLength",
    "minimum",
    "items",
    "maxItems",
    "minItems",
}
_UNSAFE_URL_RE = re.compile(r"[\x00-\x20\x7f\\]")
_CONTROL_RE = re.compile(r"[\x00-\x1f\x7f]")
BANNED_HTML_TAGS = ("link", "iframe", "object", "embed", "base")
BANNED_HTML_ATTRIBUTES = ("srcset", "action", "formaction")
_CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_CSS_URL_RE = re.compile(r"url\(\s*([^)]*)\)", re.IGNORECASE)
_CSS_IMPORT_RE = re.compile(r"@import|image-set\s*\(", re.IGNORECASE)


class SchemaError(Exception):
    """A schema file uses a keyword this checker does not implement, or cannot be read."""


def _reject_constant(name):
    raise ValueError(f"non-finite number {name} is not allowed")


def _parse_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError(f"non-finite number {text} is not allowed")
    return value


def load_json(path):
    """Read a JSON file; NaN, Infinity, -Infinity and overflowing literals raise ValueError."""
    with open(path, encoding="utf-8") as fh:
        return json.load(fh, parse_constant=_reject_constant, parse_float=_parse_float)


class Finding(NamedTuple):
    level: str
    rule: str
    where: str
    message: str

    def line(self):
        text = " ".join(str(self.message).split())
        return f"{self.level} {self.rule} {self.where}: {text}"

    def as_dict(self):
        return {
            "level": self.level,
            "rule": self.rule,
            "where": self.where,
            "message": self.message,
        }


# --- the JSON Schema subset -------------------------------------------------------------


def _type_name(value):
    if value is None:
        return "null"
    for name, kind in (
        ("boolean", bool),
        ("integer", int),
        ("number", float),
        ("string", str),
        ("array", list),
        ("object", dict),
    ):
        if isinstance(value, kind):
            return name
    return type(value).__name__


def _type_ok(value, name):
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    kinds = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}
    if name not in kinds:
        raise SchemaError(f"unsupported schema type {name!r}")
    return isinstance(value, kinds[name])


def _same(a, b):
    """Enum equality that does not let True equal 1."""
    return type(a) is type(b) and a == b


def _short(value):
    text = repr(value)
    return text if len(text) <= 60 else text[:57] + "..."


def _anchored(pattern):
    """A trailing ``$`` matches before a final newline in Python; ``\\Z`` does not."""
    if pattern.endswith("$") and not pattern.endswith("\\$"):
        return pattern[:-1] + r"\Z"
    return pattern


def _check(value, schema, path, out):
    unsupported = set(schema) - _SUPPORTED_KEYWORDS
    if unsupported:
        raise SchemaError(f"unsupported schema keyword(s) {sorted(unsupported)} at {path}")
    declared = schema.get("type")
    if declared is not None:
        names = declared if isinstance(declared, list) else [declared]
        if not any(_type_ok(value, name) for name in names):
            out.append(f"{path}: expected {'|'.join(names)}, got {_type_name(value)}")
            return
    if "enum" in schema and not any(_same(value, option) for option in schema["enum"]):
        out.append(f"{path}: {_short(value)} is not one of {schema['enum']}")
    if isinstance(value, str):
        if "pattern" in schema and not re.search(_anchored(schema["pattern"]), value):
            out.append(f"{path}: {_short(value)} does not match {schema['pattern']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            out.append(f"{path}: length {len(value)} exceeds maxLength {schema['maxLength']}")
    if _type_ok(value, "number") and "minimum" in schema and value < schema["minimum"]:
        out.append(f"{path}: {value} is below minimum {schema['minimum']}")
    if isinstance(value, list):
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            out.append(f"{path}: {len(value)} items exceeds maxItems {schema['maxItems']}")
        if "minItems" in schema and len(value) < schema["minItems"]:
            out.append(f"{path}: {len(value)} items is below minItems {schema['minItems']}")
        if "items" in schema:
            for index, item in enumerate(value):
                _check(item, schema["items"], f"{path}[{index}]", out)
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                out.append(f"{path}: missing required key '{key}'")
        properties = schema.get("properties", {})
        for key, sub in properties.items():
            if key in value:
                _check(value[key], sub, f"{path}.{key}", out)
        extra = schema.get("additionalProperties", True)
        for key in value:
            if key in properties:
                continue
            if extra is False:
                out.append(f"{path}: unknown key '{key}'")
            elif isinstance(extra, dict):
                _check(value[key], extra, f"{path}.{key}", out)


def check_schema(value, schema, path="$"):
    """Return the list of problems ``value`` has against ``schema`` (empty means valid)."""
    out = []
    _check(value, schema, path, out)
    return out


# --- small helpers ----------------------------------------------------------------------


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _numeric_keys(obj, path=""):
    found = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            here = f"{path}.{key}" if path else str(key)
            if isinstance(key, str) and key.lower() in NUMERIC_KEYS:
                found.append(here)
            found.extend(_numeric_keys(value, here))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            found.extend(_numeric_keys(value, f"{path}[{index}]"))
    return found


def _evidence_url_problem(url, docs_hosts):
    """Why ``url`` is not an https URL on one of ``docs_hosts``, or None."""
    if _UNSAFE_URL_RE.search(url):
        return "contains whitespace, a control character or a backslash"
    try:
        parts = urlsplit(url)
        host = parts.hostname
    except ValueError as exc:
        return f"is not a parseable URL ({exc})"
    if parts.scheme != "https":
        return f"scheme '{parts.scheme}' is not https"
    if host not in [h.lower() for h in docs_hosts]:
        return f"host '{host}' is not in docs_hosts {list(docs_hosts)}"
    if parts.netloc.lower() != host:
        return "has userinfo or a port"
    return None


def _html_url_problem(raw, allowed_hosts):
    """Why a rendered href or src is not relative, an anchor or an allow-listed https URL."""
    url = re.sub(r"[\t\r\n]", "", raw.strip()).replace("\\", "/")
    if url == "" or url.startswith("#"):
        return None
    if _CONTROL_RE.search(url):
        return "contains a control character"
    try:
        parts = urlsplit(url)
        host = parts.hostname
    except ValueError as exc:
        return f"is not a parseable URL ({exc})"
    if parts.scheme == "" and parts.netloc == "":
        return None
    if parts.scheme != "https":
        return f"scheme '{parts.scheme or 'protocol-relative'}' is not https"
    if host not in allowed_hosts:
        return f"host '{host}' is not on the allow-list"
    if parts.netloc.lower() != host:
        return "has userinfo or a port"
    return None


def _css_problems(text):
    """Why a style attribute or style block reaches outside the page, or [] when it does not."""
    css = _CSS_COMMENT_RE.sub(" ", text)
    out = []
    if "\\" in css:
        out.append("holds a CSS escape, which cannot be checked")
    if _CSS_IMPORT_RE.search(css):
        out.append("imports a style sheet or an image set")
    for match in _CSS_URL_RE.finditer(css):
        target = match.group(1).strip().strip("\"'").strip()
        if not (target.lower().startswith("data:") or target.startswith("#")):
            out.append(f"url({_short(target)}) points outside the page")
    return out


def _script_hash(body):
    digest = hashlib.sha256(body.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(digest).decode("ascii") + "'"


class _PageScanner(HTMLParser):
    """One pass over a page, collecting what R13 judges.

    html.parser lower-cases tag and attribute names, so every match here is case-insensitive.
    ``problems`` are findings that need no outside knowledge; ``links`` still need the host
    allow-list, and ``scripts`` the content-security policies that were in force at each one.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.problems = []
        self.links = []
        self.scripts = []
        self._policies = []
        self._script = None
        self._style = None
        self._seen = set()

    def _problem(self, message):
        if message not in self._seen:
            self._seen.add(message)
            self.problems.append(message)

    def _policy(self, content):
        for directive in content.split(";"):
            tokens = directive.split()
            if tokens and tokens[0].lower() == "script-src":
                self._policies.append(set(tokens[1:]))
                return
        self._policies.append(set())

    def _start(self, tag, attrs, closed):
        if tag in BANNED_HTML_TAGS:
            self._problem(f"<{tag}> is not allowed")
        named = {}
        for name, value in attrs:
            named.setdefault(name, value)
            if name.startswith("on"):
                self._problem(f"event-handler attribute {name} on <{tag}>")
            if name in BANNED_HTML_ATTRIBUTES:
                self._problem(f"attribute {name} on <{tag}> is not allowed")
            if name in ("href", "src") and value is not None:
                self.links.append((tag, name, value))
            if name == "style" and value:
                for problem in _css_problems(value):
                    self._problem(f"style attribute on <{tag}> {problem}")
        if tag == "script":
            if attrs:
                self._problem("<script> has attributes")
            if closed:
                self._problem("self-closing <script> is read as an open tag by browsers")
            else:
                self._script = (list(self._policies), [])
        elif tag == "style" and not closed:
            self._style = []
        elif tag == "meta":
            equiv = (named.get("http-equiv") or "").strip().lower()
            if equiv == "refresh":
                self._problem('<meta http-equiv="refresh"> is not allowed')
            elif equiv == "content-security-policy":
                self._policy(named.get("content") or "")

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs, closed=False)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, closed=True)

    def handle_endtag(self, tag):
        if tag == "script" and self._script is not None:
            policies, chunks = self._script
            self.scripts.append(("".join(chunks), policies))
            self._script = None
        elif tag == "style" and self._style is not None:
            self._finish_style()

    def handle_data(self, data):
        if self._script is not None:
            self._script[1].append(data)
        elif self._style is not None:
            self._style.append(data)

    def _finish_style(self):
        for problem in _css_problems("".join(self._style)):
            self._problem(f"<style> block {problem}")
        self._style = None

    def close(self):
        super().close()
        if self._script is not None:
            self._problem("<script> is never closed")
            self._script = None
        if self._style is not None:
            self._finish_style()


# --- the validator ----------------------------------------------------------------------


class Validator:
    def __init__(
        self,
        data_dir,
        require_complete=False,
        html_dir=None,
        schema_dir=None,
        check_repo_paths=True,
    ):
        self.data_dir = Path(data_dir)
        self.check_repo_paths = check_repo_paths
        self.require_complete = require_complete
        self.html_dir = Path(html_dir) if html_dir else None
        self.schema_dir = Path(schema_dir) if schema_dir else SCHEMA_DIR
        self.findings = []
        self.schemas = {}
        self.surfaces = {}
        self.core_rows = []
        self.row_ids = set()
        self.optional_rows = set()
        self.optional_facet_ids = set()
        self.cells = []
        self.evidence = []
        self.levers = []
        self.task_rows = []
        self.register = []
        self.snapshot = None
        self.evidence_by_id = {}
        self.cells_by_id = {}
        self.lever_keys = set()
        self._root = None
        self.summary = {}

    # reporting

    def error(self, rule, where, message):
        self.findings.append(Finding("error", rule, where, message))

    def info(self, rule, where, message):
        self.findings.append(Finding("info", rule, where, message))

    @property
    def _missing_rule(self):
        return R_COMPLETE if self.require_complete else None

    @staticmethod
    def _where(rel, rec, index):
        ident = rec.get("id") if isinstance(rec, dict) else None
        return f"{rel}#{ident}" if isinstance(ident, str) else f"{rel}#[{index}]"

    # loading

    def _load_schemas(self):
        for name in SCHEMA_NAMES:
            path = self.schema_dir / f"{name}.schema.json"
            try:
                self.schemas[name] = load_json(path)
            except (OSError, ValueError) as exc:
                raise SchemaError(f"cannot load schema {path}: {exc}") from exc
        snapshot = self.schemas["snapshot"]
        # validate.py rule 9 reads snapshot.matrix_pending, which the schema file does not
        # declare. Add it to a derived copy so an honest snapshot is not an R01 failure.
        props = dict(snapshot.get("properties", {}))
        props.setdefault("matrix_pending", {"type": "boolean"})
        self.schemas["snapshot"] = {**snapshot, "properties": props}

    def _read(self, rel, missing_rule=None):
        path = self.data_dir / rel
        if not path.is_file():
            if missing_rule:
                self.error(missing_rule, rel, "file is missing")
            return None
        size = path.stat().st_size
        if size > MAX_DATA_FILE_BYTES:
            self.error(R_SIZE, rel, f"{size} bytes exceeds the {MAX_DATA_FILE_BYTES} byte limit")
        try:
            return load_json(path)
        except (OSError, ValueError) as exc:
            self.error(R_STRUCTURE, rel, f"cannot read as JSON: {exc}")
            return None

    def _load_facets(self):
        doc = self._read("facets.json", missing_rule=R_STRUCTURE)
        if doc is None:
            return
        if not isinstance(doc, dict) or not isinstance(doc.get("facets"), list):
            self.error(R_STRUCTURE, "facets.json", "expected an object with a 'facets' list")
            return
        facet_owner, row_owner = {}, {}
        for key, optional in (("facets", False), ("optional_facets", True)):
            listed = doc.get(key)
            if listed is not None and not isinstance(listed, list):
                self.error(R_STRUCTURE, "facets.json", f"'{key}' must be a list")
                continue
            for index, facet in enumerate(listed or []):
                self._load_facet(key, index, facet, optional, facet_owner, row_owner)
        self.row_ids = self.optional_rows.union(self.core_rows)

    def _load_facet(self, key, index, facet, optional, facet_owner, row_owner):
        label = f"{key}[{index}]"
        if not isinstance(facet, dict):
            self.error(R_STRUCTURE, "facets.json", f"{label} is not an object")
            return
        facet_id = facet.get("id")
        if not _nonempty(facet_id):
            self.error(R_STRUCTURE, "facets.json", f"{label} needs a non-empty string id")
            facet_id = None
        elif facet_id in facet_owner:
            self.error(
                R_STRUCTURE,
                "facets.json",
                f"facet id {facet_id!r} in {label} is already used by {facet_owner[facet_id]}",
            )
        else:
            facet_owner[facet_id] = label
        if optional and facet_id:
            self.optional_facet_ids.add(facet_id)
        rows = facet.get("rows")
        if rows is not None and not isinstance(rows, list):
            self.error(
                R_STRUCTURE, "facets.json", f"rows of facet {facet_id or label} is not a list"
            )
            return
        for row in rows or []:
            row_id = row.get("id") if isinstance(row, dict) else None
            if not isinstance(row_id, str):
                self.error(
                    R_STRUCTURE, "facets.json", f"a row of facet {facet_id or label} has no id"
                )
                continue
            if facet_id and not row_id.startswith(f"{facet_id}."):
                self.error(
                    R_STRUCTURE,
                    "facets.json",
                    f"row {row_id!r} does not start with '{facet_id}.' (facet {facet_id})",
                )
            if row_id in row_owner:
                self.error(
                    R_STRUCTURE,
                    "facets.json",
                    f"row id {row_id!r} in facet {facet_id or label} is already used by "
                    f"facet {row_owner[row_id]}",
                )
                continue
            row_owner[row_id] = facet_id or label
            if optional:
                self.optional_rows.add(row_id)
            else:
                self.core_rows.append(row_id)

    def _load_surfaces(self):
        doc = self._read("surfaces.json", missing_rule=R_STRUCTURE)
        if doc is None:
            return
        if not isinstance(doc, dict) or not isinstance(doc.get("surfaces"), list):
            self.error(R_STRUCTURE, "surfaces.json", "expected an object with a 'surfaces' list")
            return
        for index, surface in enumerate(doc["surfaces"]):
            where = f"surfaces.json#[{index}]"
            if not isinstance(surface, dict) or not _nonempty(surface.get("id")):
                self.error(R_STRUCTURE, where, "a surface needs a non-empty string 'id'")
                continue
            hosts = surface.get("docs_hosts")
            if not isinstance(hosts, list) or not all(isinstance(h, str) for h in hosts):
                self.error(R_STRUCTURE, where, "docs_hosts must be a list of strings")
                continue
            self.surfaces[surface["id"]] = surface

    def _load_per_surface(self, folder, key):
        """Records of cells/ or evidence/ as (file, index, record, file_surface)."""
        out = []
        directory = self.data_dir / folder
        present = (
            {p.stem: p for p in sorted(directory.glob("*.json"))} if directory.is_dir() else {}
        )
        for stem in present:
            if stem not in self.surfaces:
                self.error(R_REFERENCE, f"{folder}/{stem}.json", "file name is not a surface")
        for sid in self.surfaces:
            rel = f"{folder}/{sid}.json"
            if sid not in present:
                if self.require_complete:
                    self.error(R_COMPLETE, rel, "file is missing")
                continue
            doc = self._read(rel)
            if doc is None:
                continue
            if not isinstance(doc, dict) or not isinstance(doc.get(key), list):
                self.error(R_STRUCTURE, rel, f"expected an object with a '{key}' list")
                continue
            if doc.get("surface") != sid:
                self.error(
                    R_REFERENCE, rel, f"top-level surface {doc.get('surface')!r} is not {sid!r}"
                )
            self._reject_unknown_keys(rel, doc, ("surface", key))
            out.extend((rel, i, rec, sid) for i, rec in enumerate(doc[key]))
        return out

    def _reject_unknown_keys(self, where, obj, allowed, rule=R_STRUCTURE):
        for key in obj:
            if key not in allowed:
                self.error(rule, where, f"unknown key '{key}'")

    def _load_wrapped(self, rel, keys, strict=True):
        """A single-file document holding one list per key; returns {key: [(index, rec)]}."""
        doc = self._read(rel, missing_rule=self._missing_rule)
        loaded = {key: [] for key in keys}
        if doc is None:
            return loaded
        if not isinstance(doc, dict):
            self.error(R_STRUCTURE, rel, "expected a JSON object")
            return loaded
        if strict:
            self._reject_unknown_keys(rel, doc, keys)
        for key in keys:
            if not isinstance(doc.get(key), list):
                self.error(R_STRUCTURE, rel, f"missing or non-list '{key}'")
            else:
                loaded[key] = list(enumerate(doc[key]))
        return loaded

    def _load_snapshot(self):
        doc = self._read("snapshot.json", missing_rule=self._missing_rule)
        if doc is None:
            return
        if self._structure("snapshot.json", doc, "snapshot"):
            self.snapshot = doc

    def _check_snapshot_refs(self):
        columns = (self.snapshot or {}).get("columns")
        for index, column in enumerate(columns if isinstance(columns, list) else []):
            if isinstance(column, dict):
                self._check_surface(f"snapshot.json#columns[{index}]", column.get("surface"))

    # shared checks

    def _structure(self, where, rec, kind):
        if not isinstance(rec, dict):
            self.error(R_STRUCTURE, where, f"record is {_type_name(rec)}, expected an object")
            return False
        for problem in check_schema(rec, self.schemas[kind]):
            self.error(R_STRUCTURE, where, problem)
        return True

    @staticmethod
    def _has_content(rec):
        """A record proves something only through a quote or a described span."""
        quote = rec.get("quote")
        span = rec.get("described_span")
        return (isinstance(quote, str) and bool(quote.strip())) or (
            isinstance(span, dict) and bool(span)
        )

    def _is_verified_evidence(self, evidence_id):
        rec = self.evidence_by_id.get(evidence_id)
        return (
            bool(rec)
            and rec.get("tier") in VERIFIED_TIERS
            and rec.get("quote_verified") is True
            and self._has_content(rec)
        )

    def _has_verified(self, ids):
        return any(self._is_verified_evidence(i) for i in ids)

    def _role_record_ok(self, evidence_id, verified):
        """A record that can carry a not-exposed or not-applicable claim.

        Tier E1-E4 and quote_verified not false; a verified cell needs it true. Tiers S, R and U
        never qualify, and an unverified cell may rest on quote_verified null only at E1-E4.
        """
        rec = self.evidence_by_id.get(evidence_id)
        if not rec or rec.get("tier") not in VERIFIED_TIERS or not self._has_content(rec):
            return False
        flag = rec.get("quote_verified")
        return flag is True or (flag is None and not verified)

    def _resolve_evidence(self, where, surface, refs):
        """The (field, id) pairs that name a record of ``surface``; the rest are R02 errors.

        An id that is unknown, or that names another surface's record, must never count towards
        verified or good, so callers use only what this returns.
        """
        usable = []
        for field, evidence_id in refs:
            rec = self.evidence_by_id.get(evidence_id)
            if rec is None:
                self.error(R_REFERENCE, where, f"{field} names unknown evidence id {evidence_id}")
            elif rec.get("surface") != surface:
                self.error(
                    R_REFERENCE,
                    where,
                    f"{field} cites {evidence_id}, a record of surface {rec.get('surface')!r}, "
                    f"not of {surface!r}",
                )
            else:
                usable.append((field, evidence_id))
        return usable

    def _refs_are_own_surface(self, cell):
        for _, evidence_id in self._cell_ref_fields(cell):
            rec = self.evidence_by_id.get(evidence_id)
            if rec is None or rec.get("surface") != cell.get("surface"):
                return False
        return True

    def _check_surface(self, where, surface):
        if not (isinstance(surface, str) and surface in self.surfaces):
            self.error(R_REFERENCE, where, f"surface {surface!r} is not in surfaces.json")

    def _check_numeric(self, where, rec):
        for found in _numeric_keys(rec):
            self.error(R_NUMERIC, where, f"numeric-confidence key '{found}' is not allowed")

    def _is_optional_row(self, row):
        if not isinstance(row, str):
            return False
        return row in self.optional_rows or row.split(".")[0] in self.optional_facet_ids

    def _is_known_row(self, row):
        return isinstance(row, str) and row in self.row_ids

    @staticmethod
    def _cell_ref_fields(cell):
        refs = []
        evidence = cell.get("evidence")
        for item in evidence if isinstance(evidence, list) else []:
            if isinstance(item, str):
                refs.append(("evidence", item))
        for key in ("vendor_statement", "reference_page_evidence", "na_quote"):
            if isinstance(cell.get(key), str):
                refs.append((key, cell[key]))
        return refs

    # rules per record kind

    def _index_evidence(self):
        for rel, index, rec, _ in self.evidence:
            ident = rec.get("id") if isinstance(rec, dict) else None
            if not isinstance(ident, str):
                continue
            if ident in self.evidence_by_id:
                self.error(R_REFERENCE, self._where(rel, rec, index), "duplicate evidence id")
            else:
                self.evidence_by_id[ident] = rec
        for rel, index, rec, _ in self.cells:
            ident = rec.get("id") if isinstance(rec, dict) else None
            if not isinstance(ident, str):
                continue
            if ident in self.cells_by_id:
                self.error(R_REFERENCE, self._where(rel, rec, index), "duplicate cell id")
            else:
                self.cells_by_id[ident] = rec

    def _check_evidence_record(self, rel, index, rec, file_surface):
        where = self._where(rel, rec, index)
        if not self._structure(where, rec, "evidence"):
            return
        sid = rec.get("surface")
        self._check_surface(where, sid)
        if sid != file_surface:
            self.error(R_REFERENCE, where, f"surface {sid!r} is in the {file_surface} file")
        self._check_numeric(where, rec)
        quote = rec.get("quote")
        if isinstance(quote, str) and len(quote) > 300:
            self.error(R_EVIDENCE, where, f"quote is {len(quote)} characters, limit is 300")
        if not _nonempty(rec.get("sha256")):
            self.error(R_EVIDENCE, where, "sha256 is missing")
        for key in ("context_before", "context_after"):
            if key not in rec:
                self.error(R_EVIDENCE, where, f"{key} is missing")
        known = isinstance(sid, str) and sid in self.surfaces
        hosts = self.surfaces[sid]["docs_hosts"] if known else []
        for key in ("url", "url_effective"):
            if known and isinstance(rec.get(key), str):
                problem = _evidence_url_problem(rec[key], hosts)
                if problem:
                    self.error(R_EVIDENCE, where, f"{key} {problem}")
        if rec.get("tier") in VERIFIED_TIERS and rec.get("quote_verified") is False:
            self.error(R_EVIDENCE, where, f"tier {rec['tier']} evidence has quote_verified false")
        if rec.get("described_span") and quote != "":
            self.error(R_EVIDENCE, where, "a described span requires an empty quote")
        if isinstance(quote, str) and not self._has_content(rec):
            self.error(R_EVIDENCE, where, "quote is empty and there is no described span")
        self._check_install_text(where, rec)

    def _check_install_text(self, where, rec):
        quote = rec.get("quote")
        if isinstance(quote, str) and install_text(quote):
            self.error(R_INSTALL, where, "quote stores an install or update command line verbatim")
        for key in ("context_before", "context_after"):
            listed = rec.get(key)
            lines = [x for x in listed if isinstance(x, str)] if isinstance(listed, list) else []
            windows = lines + ["\n".join(lines[i : i + 2]) for i in range(len(lines) - 1)]
            if any(install_text(w) for w in windows):
                self.error(R_INSTALL, where, f"{key} holds an install or update command line")
        locator = rec.get("locator")
        heading = locator.get("heading") if isinstance(locator, dict) else None
        if isinstance(heading, str) and install_text(heading):
            self.error(R_INSTALL, where, "locator.heading holds an install or update command line")
        span = rec.get("described_span")
        if isinstance(span, dict) and span.get("description") != INSTALL_DESCRIPTION:
            self.error(
                R_INSTALL,
                where,
                f"described_span.description must be the fixed text {INSTALL_DESCRIPTION!r}",
            )

    def _check_cell(self, rel, index, cell, file_surface):
        where = self._where(rel, cell, index)
        if not self._structure(where, cell, "cell"):
            return
        sid, row, state = cell.get("surface"), cell.get("row"), cell.get("state")
        self._check_surface(where, sid)
        if sid != file_surface:
            self.error(R_REFERENCE, where, f"surface {sid!r} is in the {file_surface} file")
        if row != "U00" and not self._is_known_row(row):
            self.error(R_REFERENCE, where, f"row {row!r} is not in facets.json")
        if row == "U00":
            # An unmapped record: the first is `<surface>/U00`, further ones `<surface>/U00/<n>`.
            if not (
                isinstance(cell.get("id"), str)
                and re.fullmatch(re.escape(f"{sid}/U00") + r"(/[0-9]+)?", cell["id"])
            ):
                self.error(R_REFERENCE, where, f"id is not '{sid}/U00' or '{sid}/U00/<n>'")
        elif cell.get("id") != f"{sid}/{row}":
            self.error(R_REFERENCE, where, f"id is not '{sid}/{row}'")
        self._check_numeric(where, cell)
        refs = self._cell_ref_fields(cell)
        usable = self._resolve_evidence(where, sid, refs)
        usable_ids = {i for _, i in usable}
        good = self._has_verified(usable_ids)
        if state in ("supported", "partial") and not good:
            self.error(R_STATE, where, f"{state} needs an E1-E4 evidence record, quote verified")
        if state == "partial" and not _nonempty(cell.get("limitation")):
            self.error(R_STATE, where, "partial needs a non-empty limitation")
        verified = cell.get("verification") == "verified"
        if state == "not-exposed":
            self._check_not_exposed(where, cell, refs, usable_ids, verified)
        if state == "not-applicable":
            if not _nonempty(cell.get("na_quote")):
                self.error(R_STATE, where, "not-applicable needs an na_quote evidence id")
            else:
                self._check_role(where, "na_quote", cell["na_quote"], usable_ids, verified)
        if state == "undocumented":
            self._check_sweep(where, cell.get("sweep_report"))
        if state == "not-researched" and not self._is_optional_row(row):
            self.error(R_STATE, where, "not-researched is allowed only on an optional facet row")
        # An undocumented cell has no evidence by definition: its proof is the sweep report,
        # which _check_sweep already enforces (positive control hit, every hit reviewed).
        if cell.get("verification") == "verified" and state != "undocumented" and not good:
            self.error(R_STATE, where, "verified needs an E1-E4 evidence record, quote verified")
        if cell.get("verification") == "unverified" and not _nonempty(cell.get("settles_by")):
            self.error(R_MARKER, where, "an unverified cell needs a non-empty settles_by")

    def _check_not_exposed(self, where, cell, refs, usable_ids, verified):
        ordinary = [i for f, i in refs if f == "evidence"]
        vendor, reference = cell.get("vendor_statement"), cell.get("reference_page_evidence")
        if not (_nonempty(vendor) or (_nonempty(reference) and ordinary)):
            self.error(
                R_STATE,
                where,
                "not-exposed needs a vendor_statement, or a reference_page_evidence "
                "plus an ordinary evidence id",
            )
            return
        if _nonempty(vendor):
            self._check_role(where, "vendor_statement", vendor, usable_ids, verified)
        if _nonempty(reference):
            self._check_role(where, "reference_page_evidence", reference, usable_ids, verified)
            if not _nonempty(vendor) and not any(
                i in usable_ids and self._role_record_ok(i, verified) for i in ordinary
            ):
                self.error(
                    R_STATE,
                    where,
                    "reference_page_evidence needs an ordinary evidence record of its own "
                    f"surface, tier E1-E4, {self._flag_text(verified)}",
                )

    @staticmethod
    def _flag_text(verified):
        return "quote_verified true" if verified else "quote_verified not false"

    def _check_role(self, where, field, evidence_id, usable_ids, verified):
        if evidence_id in usable_ids and self._role_record_ok(evidence_id, verified):
            return
        self.error(
            R_STATE,
            where,
            f"{field} {evidence_id} must be a record of the cell's surface, tier E1-E4, "
            f"{self._flag_text(verified)}",
        )

    def _check_sweep(self, where, sweep):
        if not isinstance(sweep, dict):
            self.error(R_STATE, where, "undocumented needs a sweep_report")
            return
        control = sweep.get("positive_control_hits")
        if not (_is_int(control) and control >= 1):
            self.error(R_STATE, where, "sweep_report needs positive_control_hits >= 1")
        hits, reviewed = sweep.get("hits"), sweep.get("hits_reviewed")
        if not (_is_int(hits) and _is_int(reviewed) and hits == reviewed):
            self.error(R_STATE, where, "sweep_report hits_reviewed must equal hits")

    def _check_lever(self, index, lever):
        where = self._where("levers.json", {"id": self._lever_label(lever)}, index)
        if not self._structure(where, lever, "lever"):
            return
        self._check_surface(where, lever.get("surface"))
        if not self._is_known_row(lever.get("row")):
            self.error(R_REFERENCE, where, f"row {lever.get('row')!r} is not in facets.json")
        self._check_numeric(where, lever)
        listed = lever.get("evidence")
        ids = [i for i in listed if isinstance(i, str)] if isinstance(listed, list) else []
        usable = self._resolve_evidence(where, lever.get("surface"), [("evidence", i) for i in ids])
        good = self._has_verified(i for _, i in usable)
        if lever.get("verification") == "verified" and not (good or self._swept_absence(lever)):
            self.error(R_LEVER, where, "verified lever needs an E1-E4 record, quote verified")
        if lever.get("location_kind") in POSITIVE_LOCATION_KINDS and not good:
            self.error(
                R_LEVER,
                where,
                f"location_kind {lever['location_kind']} needs a verified positive quote",
            )
        if lever.get("model_conditional") is True and not lever.get("values_by_model"):
            self.error(R_LEVER, where, "model_conditional needs a non-empty values_by_model")
        if lever.get("unread_models") and lever.get("verification") != "unverified":
            self.error(R_LEVER, where, "unread_models requires verification unverified")

    def _swept_absence(self, lever):
        """An undocumented lever record rests on its cell's sweep, not on a quote.

        The record mirrors a cell that is undocumented and verified with a sweep_report; it names no
        evidence and no location, so there is no quote for it to carry.
        """
        if lever.get("state") != "undocumented" or lever.get("location_kind") != "undocumented":
            return False
        if lever.get("evidence"):
            return False
        cell = self.cells_by_id.get(f"{lever.get('surface')}/{lever.get('row')}")
        return (
            isinstance(cell, dict)
            and cell.get("state") == "undocumented"
            and cell.get("verification") == "verified"
            and isinstance(cell.get("sweep_report"), dict)
        )

    @staticmethod
    def _lever_label(lever):
        if not isinstance(lever, dict):
            return None
        parts = [lever.get("surface"), lever.get("lever"), lever.get("row"), lever.get("model")]
        text = "/".join(str(p) for p in parts if p)
        return text or None

    def _check_task_row(self, index, row):
        where = f"levers.json#task_shape_rows[{index}]"
        if not isinstance(row, dict):
            self.error(R_STRUCTURE, where, f"record is {_type_name(row)}, expected an object")
            return
        self._check_numeric(where, row)
        self._reject_unknown_keys(where, row, TASK_ROW_KEYS, R_TASK)
        for key in ("surface", "task_class", "pointer", "basis"):
            if key not in row:
                self.error(R_TASK, where, f"missing key '{key}'")
        if "surface" in row:
            self._check_surface(where, row["surface"])
        if "task_class" in row and not _nonempty(row["task_class"]):
            self.error(R_TASK, where, "task_class must be a non-empty string")
        if "basis" in row and row["basis"] not in TASK_BASES:
            self.error(R_TASK, where, f"basis {row['basis']!r} is not one of {list(TASK_BASES)}")
        settings = row.get("lever_settings")
        if "lever_settings" in row and not isinstance(settings, list):
            self.error(R_TASK, where, "lever_settings must be a list")
        for position, setting in enumerate(settings if isinstance(settings, list) else []):
            self._check_lever_setting(f"{where}.lever_settings[{position}]", setting)
        pointer, pending = row.get("pointer"), row.get("pending_label")
        if pointer is not None and not (
            isinstance(pointer, dict)
            and _nonempty(pointer.get("file"))
            and _nonempty(pointer.get("path"))
        ):
            self.error(R_TASK, where, "pointer must be null or an object with file and path")
        elif isinstance(pointer, dict):
            self._reject_unknown_keys(f"{where}.pointer", pointer, POINTER_KEYS, R_TASK)
            self._check_pointer_file(f"{where}.pointer", pointer["file"])
        if pending is not None and not isinstance(pending, str):
            self.error(R_TASK, where, "pending_label must be a string or null")
        if pointer is None and not _nonempty(pending):
            self.error(R_TASK, where, "needs a pointer or a non-empty pending_label")
        snapshot = self.snapshot or {}
        if _nonempty(pending) and snapshot.get("matrix_pending") is not True:
            self.error(R_TASK, where, "pending_label is allowed only when matrix_pending is true")
        if pointer is not None and not _nonempty(snapshot.get("matrix_sha")):
            self.error(R_TASK, where, "a row with a pointer needs snapshot.matrix_sha")

    def _check_lever_setting(self, where, setting):
        """A lever_settings entry is ``surface|lever|model`` and names a record in levers.json."""
        if not isinstance(setting, str) or setting.count("|") != 2:
            self.error(R_TASK, where, f"{_short(setting)} is not a 'surface|lever|model' string")
        elif ref_key(setting) not in self.lever_keys:
            self.error(R_REFERENCE, where, f"{_short(setting)} names no record in levers.json")

    def _repo_root(self):
        """The repository root of the data directory, or None when there is none."""
        try:
            run = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=self.data_dir,
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError):
            run = None
        if run is not None and run.returncode == 0 and run.stdout.strip():
            return Path(run.stdout.strip())
        start = self.data_dir.resolve()
        for parent in (start, *start.parents):
            if (parent / ".git").exists():
                return parent
        return None

    def _check_pointer_file(self, where, file):
        """The pointer file is a repo-relative path inside the repository, and it exists."""
        if not self.check_repo_paths:
            return
        if self._root is None:
            self._root = self._repo_root() or False
            if not self._root:
                self.error(
                    R_REFERENCE,
                    where,
                    "cannot find the repository root to resolve pointer files; "
                    "pass --no-repo-paths to skip",
                )
        if not self._root:
            return
        relative = Path(file)
        if relative.is_absolute() or ".." in relative.parts:
            self.error(R_REFERENCE, where, f"file {file!r} is not a path inside the repository")
            return
        root = self._root.resolve()
        target = (root / relative).resolve()
        if root not in target.parents:
            self.error(R_REFERENCE, where, f"file {file!r} resolves outside the repository")
        elif not target.is_file():
            self.error(R_REFERENCE, where, f"file {file!r} does not exist in the repository")

    def _check_register_entry(self, index, entry, ranks):
        where = self._where("register.json", entry, index)
        if not self._structure(where, entry, "register"):
            return
        etype = entry.get("type")
        unsettled = []
        listed = entry.get("cells")
        for cell_id in listed if isinstance(listed, list) else []:
            cell = self.cells_by_id.get(cell_id) if isinstance(cell_id, str) else None
            if cell is None:
                self.error(R_REFERENCE, where, f"cells names unknown cell id {cell_id!r}")
            if (
                cell is None
                or cell.get("verification") != "verified"
                or not self._refs_are_own_surface(cell)
            ):
                unsettled.append(cell_id)
        for sid in entry.get("surfaces") if isinstance(entry.get("surfaces"), list) else []:
            self._check_surface(where, sid)
        for row in entry.get("rows") if isinstance(entry.get("rows"), list) else []:
            if row != "U00" and not self._is_known_row(row):
                self.error(R_REFERENCE, where, f"rows names {row!r}, which is not in facets.json")
        ceiling = entry.get("ceiling")
        if isinstance(ceiling, dict) and ceiling.get("cell") not in self.cells_by_id:
            self.error(
                R_REFERENCE, where, f"ceiling.cell names unknown cell id {ceiling.get('cell')!r}"
            )
        if unsettled and etype != "probe":
            self.error(R_REGISTER, where, f"type must be probe: unverified or missing {unsettled}")
        if etype in ("correct", "reconcile") and not isinstance(entry.get("repo_claim"), dict):
            self.error(R_REGISTER, where, f"a {etype} entry needs repo_claim")
        words = len(str(entry.get("proposal", "")).split())
        if words > MAX_PROPOSAL_WORDS:
            self.error(R_REGISTER, where, f"proposal is {words} words, limit {MAX_PROPOSAL_WORDS}")
        if entry.get("status") != "proposed":
            self.error(R_REGISTER, where, "status must be proposed")
        if _is_int(entry.get("rank")):
            ranks.setdefault(entry["rank"], []).append(where)
        files = entry.get("repo_files")
        for item in files if isinstance(files, list) else []:
            if (
                isinstance(item, dict)
                and item.get("exists") is False
                and etype not in NEW_FILE_TYPES
            ):
                self.error(
                    R_REGISTER,
                    where,
                    f"repo_files {item.get('path')!r} does not exist; only "
                    f"{list(NEW_FILE_TYPES)} may name a new file",
                )

    def _check_completeness(self):
        present = Counter(
            (rec.get("surface"), rec.get("row"))
            for _, _, rec, _ in self.cells
            if isinstance(rec, dict)
        )
        for sid in self.surfaces:
            missing = [row for row in self.core_rows if present[(sid, row)] == 0]
            self.summary.setdefault(sid, {})["missing"] = len(missing)
            if missing:
                self.error(
                    R_COMPLETE,
                    f"cells/{sid}.json",
                    f"{len(missing)} of {len(self.core_rows)} frozen rows have no cell "
                    f"(first: {', '.join(missing[:5])})",
                )
            for row in self.core_rows:
                if present[(sid, row)] > 1:
                    self.error(R_COMPLETE, f"cells/{sid}.json", f"row {row} has more than one cell")
        for rel, index, cell, _ in self.cells:
            if (
                isinstance(cell, dict)
                and cell.get("state") == "not-researched"
                and cell.get("row") in self.core_rows
            ):
                self.error(
                    R_COMPLETE,
                    self._where(rel, cell, index),
                    "only optional facet rows may be not-researched",
                )

    def _check_html(self):
        root = self.html_dir
        if root is None:
            return
        if not root.is_dir():
            self.error(R_HTML, str(root), "html directory does not exist")
            return
        hosts = {h.lower() for s in self.surfaces.values() for h in s["docs_hosts"]}
        hosts.update(EXTRA_HTML_HOSTS)
        total = 0
        for path in sorted(root.rglob("*.html")):
            rel = path.relative_to(root).as_posix()
            size = path.stat().st_size
            total += size
            if size > MAX_HTML_PAGE_BYTES:
                self.error(R_SIZE, rel, f"{size} bytes exceeds the {MAX_HTML_PAGE_BYTES} limit")
            text = path.read_bytes().decode("utf-8", errors="replace")
            scanner = _PageScanner()
            scanner.feed(text)
            scanner.close()
            for problem in scanner.problems:
                self.error(R_HTML, rel, problem)
            for tag, name, url in scanner.links:
                problem = _html_url_problem(url, hosts)
                if problem:
                    self.error(R_HTML, rel, f"<{tag} {name}={_short(url)}> {problem}")
            for body, policies in scanner.scripts:
                self._check_script(rel, body, policies)
        if total > MAX_HTML_TOTAL_BYTES:
            self.error(R_SIZE, str(root), f"{total} bytes of HTML exceeds {MAX_HTML_TOTAL_BYTES}")

    def _check_script(self, rel, body, policies):
        """An inline script runs only if every policy already parsed lists its exact hash."""
        token = _script_hash(body)
        if not policies:
            self.error(R_HTML, rel, "an inline <script> runs under no content-security policy")
        elif any(token not in sources for sources in policies):
            self.error(R_HTML, rel, f"an inline <script> hash {token} is not in script-src")

    def _summarize(self):
        for sid in self.surfaces:
            self.summary.setdefault(sid, {})
        for _, _, cell, sid in self.cells:
            if not isinstance(cell, dict):
                continue
            counts = self.summary.setdefault(sid, {})
            counts["cells"] = counts.get("cells", 0) + 1
            for key in ("state", "verification"):
                label = f"{key}:{cell.get(key)}"
                counts[label] = counts.get(label, 0) + 1
        for sid, counts in self.summary.items():
            counts.setdefault("cells", 0)
            fields = " ".join(f"{k}={counts[k]}" for k in sorted(counts))
            self.info("summary", sid, fields)

    # orchestration

    def run(self):
        self._load_schemas()
        self._load_facets()
        self._load_surfaces()
        self.cells = self._load_per_surface("cells", "cells")
        self.evidence = self._load_per_surface("evidence", "evidence")
        levers_doc = self._load_wrapped("levers.json", ("levers", "task_shape_rows"))
        self.levers = levers_doc["levers"]
        self.task_rows = levers_doc["task_shape_rows"]
        self.register = self._load_wrapped("register.json", ("entries",), strict=False)["entries"]
        self._load_snapshot()
        self._index_evidence()
        self.lever_keys = {
            lever_key(lv.get("surface"), lv.get("lever"), lv.get("model"))
            for _, lv in self.levers
            if isinstance(lv, dict)
        }
        self._check_snapshot_refs()
        for rel, index, rec, sid in self.evidence:
            self._check_evidence_record(rel, index, rec, sid)
        for rel, index, rec, sid in self.cells:
            self._check_cell(rel, index, rec, sid)
        for index, lever in self.levers:
            self._check_lever(index, lever)
        for index, row in self.task_rows:
            self._check_task_row(index, row)
        ranks = {}
        for index, entry in self.register:
            self._check_register_entry(index, entry, ranks)
        for rank, wheres in ranks.items():
            if len(wheres) > 1:
                self.error(R_REGISTER, wheres[1], f"rank {rank} is not unique ({len(wheres)} uses)")
        if self.require_complete:
            self._check_completeness()
        self._check_html()
        self._summarize()
        return self.findings


def validate(
    data_dir=None, require_complete=False, html_dir=None, schema_dir=None, check_repo_paths=True
):
    """Run every rule; returns (findings, per-surface summary)."""
    validator = Validator(
        data_dir or DATA_DIR, require_complete, html_dir, schema_dir, check_repo_paths
    )
    return validator.run(), validator.summary


# --- self-test and CLI ------------------------------------------------------------------


def _selftest():
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["a"],
        "properties": {
            "a": {"type": "string", "pattern": "^x[0-9]$", "maxLength": 2},
            "n": {"type": "integer", "minimum": 1},
            "l": {"type": "array", "minItems": 1, "maxItems": 2, "items": {"enum": [1, 2]}},
        },
    }
    if check_schema({"a": "x1", "n": 1, "l": [1, 2]}, schema):
        raise AssertionError("a valid record was rejected")
    bad = {"a": "x1\n", "n": True, "l": [True], "z": 0}
    if len(check_schema(bad, schema)) < 4:
        raise AssertionError("an invalid record was not fully rejected")
    try:
        check_schema({}, {"oneOf": []})
    except SchemaError:
        pass
    else:
        raise AssertionError("an unsupported keyword was not rejected")
    if _evidence_url_problem("https://docs.x.ai/a", ["docs.x.ai"]):
        raise AssertionError("an allow-listed URL was rejected")
    if not _evidence_url_problem("http://docs.x.ai/a", ["docs.x.ai"]):
        raise AssertionError("a non-https URL was accepted")
    if not _html_url_problem("//evil.example/x", {"github.com"}):
        raise AssertionError("a protocol-relative URL was accepted")
    if _html_url_problem("#top", set()) or _html_url_problem("a/b.html", set()):
        raise AssertionError("a relative URL was rejected")
    if _numeric_keys({"a": [{"Confidence": 1}]}) != ["a[0].Confidence"]:
        raise AssertionError("a nested numeric-confidence key was missed")
    if not _evidence_url_problem("https://docs.x.ai:8443/a", ["docs.x.ai"]):
        raise AssertionError("a URL with a port was accepted")
    if not _css_problems("a{background:url(https://evil.example/x)}") or _css_problems(
        "a{fill:url(#g)}"
    ):
        raise AssertionError("a CSS url was misjudged")
    with tempfile.TemporaryDirectory() as tmp:
        findings, _ = validate(tmp)
        if not any(f.rule == R_STRUCTURE and f.where == "facets.json" for f in findings):
            raise AssertionError("an empty data directory did not report facets.json")
    print("OK")


def main(argv=None):
    # read-only: it needs no tree pin, so it also runs on main after the branch lands
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data-dir", default=str(DATA_DIR))
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--html-dir")
    parser.add_argument(
        "--no-repo-paths",
        action="store_true",
        help="do not resolve task-row pointer files against the repository (temp-dir tests)",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0
    try:
        findings, summary = validate(
            args.data_dir,
            args.require_complete,
            args.html_dir,
            check_repo_paths=not args.no_repo_paths,
        )
    except SchemaError as exc:
        print(f"error {R_STRUCTURE} schemas: {exc}")
        return 2
    errors = sum(1 for f in findings if f.level == "error")
    if args.json:
        doc = {"errors": errors, "findings": [f.as_dict() for f in findings], "summary": summary}
        print(json.dumps(doc, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        for finding in findings:
            print(finding.line())
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
