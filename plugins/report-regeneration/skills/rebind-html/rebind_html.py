#!/usr/bin/env python3
"""
rebind_html.py — report-regeneration pipeline stage 3, the HTML surgical output engine
(the `rebind-html` skill).

Applies a Binding Manifest (`knowledge/binding-manifest.schema.json`) to a COPY of an HTML
template (`knowledge/core-architecture-spec.md` §1 "surgeon, not a renderer") and emits the
regenerated HTML. Per §4's node taxonomy:

    frozen       — leave byte-identical. EARNED, never assumed: this script does not
                   decide a node is frozen (that is the manifest's job, from an earlier
                   pipeline stage) — it only proves, after every other binding has been
                   applied, that a frozen node's bytes did not move.
    surgical     — strip the old value first (zero-literal construction), THEN write the
                   new value at the anchor. The strip and the write are two separate
                   mutations, in that order, so at the instant between them the node
                   provably carries no old instance value — by construction, not by a
                   downstream check.
    regenerate   — rebuilt from new data via stdlib string templating (`string.Template`,
                   dotted-placeholder subclass) with jinja2 as OPTIONAL acceleration for
                   templates that use native Jinja control syntax (imported gracefully;
                   every ${dotted.path}-only template works with jinja2 absent). Same
                   strip-then-write zero-literal construction as surgical. A raster/void
                   node (an <img>) is rebound by attribute (src/alt), never by transplant.
    needs-review — left in place, untouched, but flagged with a visible on-page badge +
                   a machine-readable `data-rebind-flag` attribute, and logged. Never
                   silently shipped.

Usage:
    python3 rebind_html.py --template t.html --manifest m.json --new-data data.json --out out.html
    python3 rebind_html.py --template t.html --manifest m.json --new-data data.json --out out.html --pretty

Exit codes:
    0 — success (output written; a JSON change-manifest printed to stdout)
    2 — usage / path-guard / manifest-schema / anchor-not-found / missing-data-query /
        missing-new-data-key error (message on stderr + a best-effort JSON error object
        on stdout, so a caller parsing stdout never gets truncated JSON — see `_emit_error`)

Design constraints (binding):
    - stdlib-first: argparse, html.parser, json, re, string, pathlib, sys. NO pip installs.
      jinja2 is OPTIONAL acceleration only, imported via a graceful try/except — every code
      path that does not need Jinja control syntax works with jinja2 absent.
    - Runs unmodified on Python 3.9.6: `from __future__ import annotations`; no PEP 604
      union syntax (`X | Y`) anywhere, no `match` statement.
    - Path-guarded (mirrors ../../scripts/seed_defects.py / ravenclaude-core's
      skills/svg-report-lint/lint.py `_repo_root()`/`_safe_path()` convention): every one
      of --template/--manifest/--new-data/--out must be a relative path, no '..'
      traversal, and must resolve inside the repo root. `--out` may never equal
      `--template` (this script works on a COPY; the template is never mutated).
    - No network calls, no subprocess.
    - Never lets an old instance value survive a surgical/regenerate node by construction
      (the strip-then-write ordering above), and never silently drops a needs-review flag.

The corpus this script is exercised against is
tests/fixtures/report-regeneration/sample-report.html (read that file's own header comment
for the taint dictionary + the data-role/data-bind/data-shape/data-period attribute
convention this engine's test suite mirrors). Full architecture: ../../knowledge/
core-architecture-spec.md §1/§4; manifest shape: ../../knowledge/
binding-manifest.schema.json.
"""
from __future__ import annotations

import argparse
import html.parser
import json
import re
import string
import sys
from pathlib import Path

try:
    import jinja2  # optional acceleration only — every stdlib-only template still works
except ImportError:  # pragma: no cover - exercised whenever jinja2 isn't installed
    jinja2 = None

# The SHARED anchor resolver (../../scripts/rr_anchor.py) — the single abstraction every stage
# lowers onto so rebind resolves the SAME compound css_selector anchors infer emits for id-less
# nodes (e.g. "#sec-appendix > h2:nth-of-type(1)"), not just element_id / simple "#id".
_SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
import rr_anchor  # noqa: E402

SCHEMA = "report-regeneration/rebind-html@1"
VALID_CLASSES = ("frozen", "surgical", "regenerate", "needs-review")


class RebindError(Exception):
    """Raised for any anchor-not-found, unsupported-anchor-kind, manifest-schema
    violation, missing-data-query, missing-new-data-key, or path-guard failure. Every
    raise here means "abort the whole run, write nothing" — never a partial or guessed
    rebind (the same never-silently-no-op discipline as seed_defects.py's
    SeedDefectError)."""


# ── path safety (mirrors ../../scripts/seed_defects.py's _repo_root()/_guard_path()) ──


def _repo_root() -> Path:
    here = Path(__file__).resolve().parent
    root = here
    for _ in range(10):
        if (root / ".repo-layout.json").is_file() or (root / "AGENTS.md").is_file():
            return root
        if root.parent == root:
            break
        root = root.parent
    # Fallback: this file lives at plugins/report-regeneration/skills/rebind-html/rebind_html.py
    return (here / ".." / ".." / ".." / "..").resolve()


def _guard_path(raw: str, *, must_exist: bool) -> Path:
    """Resolve `raw` and reject traversal / absolute-escape. Never touches the filesystem
    outside the repo root. Raises RebindError (never a bare OSError) on any violation."""
    if not raw:
        raise RebindError("empty path")
    p = Path(raw)
    if p.is_absolute():
        raise RebindError(f"absolute paths are not allowed: {raw!r}")
    if ".." in p.parts:
        raise RebindError(f"path traversal ('..') is not allowed: {raw!r}")
    repo_root = _repo_root().resolve()
    resolved = (Path.cwd() / p).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise RebindError(f"path escapes the repo root: {resolved}") from exc
    if must_exist and not resolved.is_file():
        raise RebindError(f"input file not found: {raw!r} (resolved {resolved})")
    return resolved


# ── generic id-anchored mutation helpers (regex/string based, deliberately not a full ──
# ── DOM rebuild — this is a surgical byte-editor over the real artifact, per §1) ──


def _id_anchor(elem_id: str) -> dict:
    return {"kind": "element_id", "value": elem_id}


def _escape_inner(value: str) -> str:
    """HTML-escape a value written into a node's inner content (P3 #16), for parity with the Office
    engine and to keep an untrusted new-data literal (`<script>`, `&`, `>`) from breaking out of its
    element. Element-content escaping only (`&`, `<`, `>`); attribute quotes are handled separately
    by the attribute-write path."""
    return html.escape(str(value), quote=False)


def _open_tag_pattern(elem_id: str) -> re.Pattern:
    """Matches ONLY the opening tag carrying id=elem_id — works for void elements
    (<img>, <br>) and for the opening tag of a paired element alike."""
    return re.compile(r'<[a-zA-Z][\w-]*\b[^>]*\bid="' + re.escape(elem_id) + r'"[^>]*>')


def _open_tag_search(html_text: str, elem_id: str):
    return _open_tag_pattern(elem_id).search(html_text)


def _open_tag_by_id(html_text: str, elem_id: str):
    m = _open_tag_search(html_text, elem_id)
    if not m:
        raise RebindError(f"anchor id={elem_id!r} not found in template")
    return m


def node_exists(html_text: str, elem_id: str) -> bool:
    return rr_anchor.exists(html_text, _id_anchor(elem_id))


def is_paired_node(html_text: str, elem_id: str) -> bool:
    """True if id=elem_id carries both an opening AND a matching closing tag (a text
    node we can strip/write inner content on). False for a void element (e.g. <img>).
    Resolved via the shared rr_anchor tree (P3 #10) so a node NESTING the same tag inside
    itself is handled by real tree structure, not a first-`</tag>` regex that truncates."""
    node = rr_anchor.try_resolve(html_text, _id_anchor(elem_id))
    return node is not None and node.is_paired


def full_node_text(html_text: str, elem_id: str) -> str:
    """The complete node span for id=elem_id — open+inner+close for a paired element, or just the
    opening tag for a void one. Resolved via rr_anchor's tree (P3 #10: same-tag nesting no longer
    truncates the span). Used for the post-hoc frozen byte-identity proof; raises RebindError if the
    anchor is missing entirely."""
    node = rr_anchor.try_resolve(html_text, _id_anchor(elem_id))
    if node is None:
        raise RebindError(f"anchor id={elem_id!r} not found in template")
    return node.outer_text(html_text)


def strip_inner_by_id(html_text: str, elem_id: str) -> tuple[str, str]:
    """STEP 1 of zero-literal construction for a text node: empty the inner content of
    id=elem_id. Returns (html_with_empty_inner, old_inner). Resolved via rr_anchor (P3 #10) so the
    inner span is the REAL element boundary even when a same-tag element nests inside it (the old
    `(.*?)</tag>` regex stopped at the first nested close and truncated the strip). Raises
    RebindError if elem_id has no paired open/close tags (a void element — use strip_attr_by_id)."""
    node = rr_anchor.try_resolve(html_text, _id_anchor(elem_id))
    if node is None:
        raise RebindError(f"anchor id={elem_id!r} not found in template")
    if not node.is_paired:
        raise RebindError(
            f"anchor id={elem_id!r} has no paired open/close tags (void element?) — "
            f"text strip/write only applies to a node with inner content"
        )
    old_inner = node.inner_text(html_text)
    new_html = html_text[: node.inner_start] + html_text[node.inner_end:]
    return new_html, old_inner


def write_inner_by_id(html_text: str, elem_id: str, new_value: str) -> str:
    """STEP 2 of zero-literal construction for a text node: write `new_value` (HTML-escaped, P3 #16)
    into the inner slot of id=elem_id. Resolved via rr_anchor's tree (P3 #10)."""
    try:
        return rr_anchor.replace_inner(html_text, _id_anchor(elem_id), _escape_inner(new_value))
    except rr_anchor.AnchorError as exc:
        raise RebindError(f"anchor id={elem_id!r} not writable: {exc}") from exc


def _read_attr(tag_text: str, name: str) -> str:
    m = re.search(r'\b' + re.escape(name) + r'="([^"]*)"', tag_text)
    return m.group(1) if m else ""


def _inject_attr_into_open_tag(open_tag_text: str, name: str, value: str) -> str:
    """Add-or-replace a single attribute directly on a captured `<tag ...>` (or
    self-closed `<tag ... />`) string, preserving the self-closing slash if present."""
    body = open_tag_text[:-1]  # strip the trailing '>'
    self_closing = body.rstrip().endswith("/")
    if self_closing:
        body = body.rstrip()[:-1].rstrip()
    pattern = re.compile(r'\b' + re.escape(name) + r'="[^"]*"')
    if pattern.search(body):
        body = pattern.sub(f'{name}="{value}"', body, count=1)
    else:
        body = body + f' {name}="{value}"'
    return body + (" />" if self_closing else ">")


def strip_attr_by_id(html_text: str, elem_id: str, attr: str) -> tuple[str, str]:
    """STEP 1 of zero-literal construction for an attribute (e.g. a raster's `src`):
    empty attribute `attr` on the opening tag carrying id=elem_id."""
    m = _open_tag_by_id(html_text, elem_id)
    old_value = _read_attr(m.group(0), attr)
    new_tag = _inject_attr_into_open_tag(m.group(0), attr, "")
    return html_text[: m.start()] + new_tag + html_text[m.end():], old_value


def write_attr_by_id(html_text: str, elem_id: str, attr: str, value: str) -> str:
    """STEP 2: write `value` into attribute `attr` on the opening tag carrying
    id=elem_id."""
    m = _open_tag_by_id(html_text, elem_id)
    new_tag = _inject_attr_into_open_tag(m.group(0), attr, value)
    return html_text[: m.start()] + new_tag + html_text[m.end():]


def _needs_review_badge(confidence, note: str) -> str:
    return (
        '<span class="rebind-needs-review-badge" data-rebind-flag="needs-review" '
        f'data-rebind-confidence="{confidence}" role="note">'
        f"⚠ NEEDS REVIEW — human sign-off required ({note})</span>"
    )


def flag_needs_review(html_text: str, elem_id: str, confidence, note: str) -> str:
    """Leaves id=elem_id's existing content/attributes completely UNTOUCHED and adds:
    (1) a machine-readable `data-rebind-flag="needs-review"` (+ confidence) attribute on
    its opening tag, and (2) a visible on-page badge — inserted as the first child for a
    paired (text) node, or as a sibling immediately following the tag for a void one.
    Never ships silently: this is guarantee #2 (every low-confidence / data-shaped-literal
    classification is surfaced for human review) made mechanical for HTML output."""
    badge = _needs_review_badge(confidence, note)
    m = _open_tag_by_id(html_text, elem_id)
    new_tag = _inject_attr_into_open_tag(m.group(0), "data-rebind-flag", "needs-review")
    new_tag = _inject_attr_into_open_tag(new_tag, "data-rebind-confidence", str(confidence))
    html_text = html_text[: m.start()] + new_tag + html_text[m.end():]

    # Insert the badge as the first child of a PAIRED node — the open-tag end resolved via the
    # rr_anchor tree (P3 #10) so a nested same-tag element inside the node can't mis-place it.
    node = rr_anchor.try_resolve(html_text, _id_anchor(elem_id))
    if node is not None and node.is_paired:
        insert_at = node.inner_start  # immediately after the (now-flagged) opening tag
        return html_text[:insert_at] + badge + html_text[insert_at:]

    m2 = _open_tag_by_id(html_text, elem_id)  # re-locate after the attribute edit above
    return html_text[: m2.end()] + badge + html_text[m2.end():]


# ── rr_anchor-backed helpers for the COMPOUND css_selector anchors infer emits for id-less ──
# ── nodes. Same visible behavior as the id-based helpers above, but located via the shared ──
# ── resolver (spans) rather than the id regex. ──


def _selector_node(html_text: str, anchor: dict):
    try:
        return rr_anchor.resolve(html_text, anchor)
    except rr_anchor.AnchorError as exc:
        raise RebindError(
            f"anchor {anchor.get('value')!r} not resolvable by rr_anchor: {exc}"
        ) from exc


def flag_needs_review_selector(html_text: str, anchor: dict, confidence, note: str) -> str:
    """flag_needs_review for a compound-css_selector-anchored (id-less) node, via rr_anchor."""
    node = _selector_node(html_text, anchor)
    new_tag = _inject_attr_into_open_tag(node.open_tag_text(html_text), "data-rebind-flag", "needs-review")
    new_tag = _inject_attr_into_open_tag(new_tag, "data-rebind-confidence", str(confidence))
    html_text = html_text[: node.open_start] + new_tag + html_text[node.open_end:]
    node2 = _selector_node(html_text, anchor)  # re-resolve after the open-tag length changed
    badge = _needs_review_badge(confidence, note)
    insert_at = node2.inner_start if node2.is_paired else node2.outer_end
    return html_text[:insert_at] + badge + html_text[insert_at:]


def apply_surgical_selector(html_text: str, anchor: dict, resolved):
    """apply_surgical for a compound-anchored paired (text) node, via rr_anchor. Same
    strip-then-write zero-literal construction as the id path."""
    node = _selector_node(html_text, anchor)
    if not node.is_paired:
        raise RebindError(
            f"surgical anchor {anchor.get('value')!r} is a compound-anchored void element — "
            f"value nodes carry element ids in this pipeline"
        )
    new_value = resolved if isinstance(resolved, str) else json.dumps(resolved)
    old_inner = node.inner_text(html_text)
    html_text = rr_anchor.replace_inner(html_text, anchor, "")  # STEP 1: strip
    html_text = rr_anchor.replace_inner(html_text, anchor, _escape_inner(new_value))  # STEP 2: write
    return html_text, old_inner


def apply_regenerate_selector(html_text: str, anchor: dict, resolved, new_data):
    """apply_regenerate for a compound-anchored paired (text) node, via rr_anchor."""
    node = _selector_node(html_text, anchor)
    if not node.is_paired:
        raise RebindError(
            f"regenerate anchor {anchor.get('value')!r} is a compound-anchored void/raster "
            f"element — rasters carry element ids in this pipeline"
        )
    if isinstance(resolved, str):
        rendered = render_template(resolved, new_data)
    elif isinstance(resolved, dict) and "template" in resolved:
        rendered = render_template(resolved["template"], new_data)
    elif isinstance(resolved, (int, float, bool)):
        rendered = json.dumps(resolved)
    else:
        raise RebindError(
            f"regenerate anchor {anchor.get('value')!r} (text) needs a template string or a "
            f'{{"template": "..."}} object from new-data; resolved value was {resolved!r}'
        )
    old_inner = node.inner_text(html_text)
    html_text = rr_anchor.replace_inner(html_text, anchor, "")
    html_text = rr_anchor.replace_inner(html_text, anchor, _escape_inner(rendered))
    return html_text, old_inner, rendered


# ── new-data resolution (dot-path lookup shared by surgical value fetch + regenerate ──
# ── template substitution) ──


def lookup_path(data, dotted_path: str):
    # Cross-stage contract (P3 #16): ALSO accept the fidelity harness's FLAT new-data schema —
    # {"values": {"<dotted.expr>": {"value": ..., "type": ...}}} — where the whole dotted expression
    # is a single key into `values` and the cell is a {value,...} object. Returning that cell's
    # `value` lets ONE new-data file flow through BOTH the harness and this rebind stage. The nested
    # dot-path schema below is unchanged, so an existing nested new-data file still works.
    if isinstance(data, dict) and isinstance(data.get("values"), dict) and dotted_path in data["values"]:
        entry = data["values"][dotted_path]
        if isinstance(entry, dict) and "value" in entry:
            return entry["value"]
        return entry
    cur = data
    for part in dotted_path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            raise RebindError(
                f"new-data has no value at path {dotted_path!r} (missing segment {part!r})"
            )
    return cur


class _DotLookup:
    """dict-like adapter so string.Template.safe_substitute can resolve dotted
    placeholders (${a.b.c}) against a nested new-data JSON object."""

    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return lookup_path(self._data, key)


class _DottedTemplate(string.Template):
    idpattern = r"[_a-zA-Z][_a-zA-Z0-9]*(?:\.[_a-zA-Z][_a-zA-Z0-9]*)*"


def render_template(template_text: str, data) -> str:
    """Render a regenerate-class template against new_data. `${dotted.path}`
    placeholders ALWAYS work via stdlib string.Template (the dotted-idpattern subclass
    above) — this path needs no third-party package and is what every test in this
    plugin exercises. If the template text ALSO uses native Jinja control syntax
    (`{{ }}` / `{% %}`, for loops/conditionals stdlib templating cannot express), jinja2
    is imported gracefully to render that richer subset; its absence in THAT case is a
    loud RebindError, never a silent stdlib mis-render of control-flow syntax."""
    needs_jinja = ("{{" in template_text) or ("{%" in template_text)
    if needs_jinja:
        if jinja2 is None:
            raise RebindError(
                "template uses Jinja control syntax ({{ }} / {% %}) but jinja2 is not "
                "installed in this environment — install jinja2, or rewrite the template "
                "using only ${dotted.path} placeholders (stdlib-only path)"
            )
        env = jinja2.Environment(autoescape=False, undefined=jinja2.StrictUndefined)
        try:
            return env.from_string(template_text).render(**data)
        except jinja2.exceptions.TemplateError as exc:
            raise RebindError(f"jinja2 template render failed: {exc}") from exc
    return _DottedTemplate(template_text).safe_substitute(_DotLookup(data))


# ── per-class rebind logic ──


def apply_surgical(html_text: str, elem_id: str, resolved) -> tuple[str, str]:
    """Zero-literal construction, two-step: STRIP the old value to empty, THEN WRITE the
    new value. At the instant between the two calls the node carries no old instance
    value — by construction, not by a downstream check."""
    if is_paired_node(html_text, elem_id):
        new_value = resolved if isinstance(resolved, str) else json.dumps(resolved)
        html_text, old_inner = strip_inner_by_id(html_text, elem_id)
        html_text = write_inner_by_id(html_text, elem_id, new_value)
        return html_text, old_inner
    if isinstance(resolved, dict) and "attr" in resolved and "value" in resolved:
        html_text, old_value = strip_attr_by_id(html_text, elem_id, resolved["attr"])
        html_text = write_attr_by_id(html_text, elem_id, resolved["attr"], resolved["value"])
        return html_text, old_value
    raise RebindError(
        f"surgical anchor id={elem_id!r} is a void element; new-data must resolve to "
        f'{{"attr": "...", "value": "..."}} to name which attribute to rebind'
    )


def apply_regenerate(html_text: str, elem_id: str, resolved, new_data) -> tuple[str, str, str]:
    """Same zero-literal construction invariant as surgical. A raster/void node (an
    <img>) is rebound by attribute (src, + alt if provided) — never by transplanting the
    old binary, per the architecture spec's construction rule (§4): "any node that
    renders as a raster ... MUST be regenerate ... a transplanted binary blob cannot be
    proven data-free"."""
    if is_paired_node(html_text, elem_id):
        if isinstance(resolved, str):
            rendered = render_template(resolved, new_data)
        elif isinstance(resolved, dict) and "template" in resolved:
            rendered = render_template(resolved["template"], new_data)
        elif isinstance(resolved, (int, float, bool)):
            rendered = json.dumps(resolved)
        else:
            raise RebindError(
                f"regenerate anchor id={elem_id!r} (text) needs a template string or a "
                f'{{"template": "..."}} object from new-data; resolved value was {resolved!r}'
            )
        html_text, old_inner = strip_inner_by_id(html_text, elem_id)
        html_text = write_inner_by_id(html_text, elem_id, rendered)
        return html_text, old_inner, rendered

    if isinstance(resolved, str):
        asset = {"src": resolved}
    elif isinstance(resolved, dict):
        asset = resolved
    else:
        raise RebindError(
            f"regenerate anchor id={elem_id!r} (raster) needs a src string or a "
            f'{{"src": ..., "alt": ...}} object from new-data'
        )
    if "src" not in asset:
        raise RebindError(f"regenerate anchor id={elem_id!r}: resolved asset has no 'src'")

    html_text, old_src = strip_attr_by_id(html_text, elem_id, "src")
    html_text = write_attr_by_id(html_text, elem_id, "src", asset["src"])
    old_repr = f"src={old_src!r}"
    new_repr = {"src": asset["src"]}
    if "alt" in asset:
        html_text, old_alt = strip_attr_by_id(html_text, elem_id, "alt")
        html_text = write_attr_by_id(html_text, elem_id, "alt", asset["alt"])
        old_repr += f", alt={old_alt!r}"
        new_repr["alt"] = asset["alt"]
    return html_text, old_repr, json.dumps(new_repr)


def resolve_anchor(anchor: dict):
    """Classify an anchor (in infer's grammar) into how rebind should locate it:
      ('id', "<element-id>")   — element_id, or a simple '#element-id' css_selector: the fast
                                 id-regex helpers handle it (unchanged).
      ('selector', anchor)     — a COMPOUND css_selector infer emits for an id-less node
                                 (e.g. "#sec-appendix > h2:nth-of-type(1)"): the rr_anchor
                                 helpers handle it.
    Raises RebindError for a genuinely malformed anchor."""
    kind = anchor.get("kind")
    value = anchor.get("value", "")
    if kind == "element_id":
        return ("id", value)
    if kind == "css_selector":
        m = re.match(r"^#([A-Za-z][\w-]*)$", value or "")
        if m:
            return ("id", m.group(1))
        if value:
            return ("selector", anchor)
    raise RebindError(
        f"anchor kind {kind!r} (value {value!r}) is not resolvable by rebind-html — expected "
        f"'element_id' or a 'css_selector' in infer's grammar"
    )


def apply_binding(html_text: str, binding: dict, new_data, changes: list) -> str:
    anchor = binding["anchor"]
    kind, ref = resolve_anchor(anchor)
    is_sel = kind == "selector"
    label = anchor.get("value") if is_sel else ref  # the human/log identity for this node
    cls = binding["class"]

    if cls == "frozen":
        present = rr_anchor.exists(html_text, anchor) if is_sel else node_exists(html_text, ref)
        if not present:
            raise RebindError(f"frozen node {label!r} not found in template")
        # A frozen binding needs NO edit — rebind leaves it byte-identical (the anchor is only
        # resolved to PROVE the node exists; never a failure on a resolvable frozen anchor).
        changes.append({
            "node_id": binding.get("node_id"),
            "anchor": label,
            "class": cls,
            "action": "no-op (frozen — earned, must stay byte-identical)",
        })
        return html_text

    if cls == "needs-review":
        confidence = binding.get("confidence")
        note = f"confidence {confidence}"
        if is_sel:
            html_text = flag_needs_review_selector(html_text, anchor, confidence, note)
        else:
            html_text = flag_needs_review(html_text, ref, confidence, note)
        changes.append({
            "node_id": binding.get("node_id"),
            "anchor": label,
            "class": cls,
            "action": "flagged needs-review (content left untouched)",
            "confidence": confidence,
        })
        return html_text

    data_query = binding.get("data_query")
    if not data_query:
        raise RebindError(f"node {label!r}: class {cls!r} requires a data_query (schema violation)")
    expr = data_query.get("expression")
    if not expr:
        raise RebindError(f"node {label!r}: data_query has no expression")
    resolved = lookup_path(new_data, expr)

    if cls == "surgical":
        if is_sel:
            html_text, old_value = apply_surgical_selector(html_text, anchor, resolved)
        else:
            html_text, old_value = apply_surgical(html_text, ref, resolved)
        changes.append({
            "node_id": binding.get("node_id"),
            "anchor": label,
            "class": cls,
            "action": "surgical-rebind (strip-then-write)",
            "old_value": old_value,
            "new_value": resolved,
        })
        return html_text

    # regenerate
    if is_sel:
        html_text, old_value, new_value = apply_regenerate_selector(html_text, anchor, resolved, new_data)
    else:
        html_text, old_value, new_value = apply_regenerate(html_text, ref, resolved, new_data)
    changes.append({
        "node_id": binding.get("node_id"),
        "anchor": label,
        "class": cls,
        "action": "regenerated (strip-then-write)",
        "old_value": old_value,
        "new_value": new_value,
    })
    return html_text


def _assert_frozen_unchanged(original_html: str, final_html: str, bindings: list) -> None:
    """Post-hoc proof, not a hope: for every frozen binding, the exact span this engine
    would emit as that node is byte-identical between the template and the output."""
    for binding in bindings:
        if binding["class"] != "frozen":
            continue
        anchor = binding["anchor"]
        kind, ref = resolve_anchor(anchor)
        if kind == "selector":
            before_node = rr_anchor.try_resolve(original_html, anchor)
            after_node = rr_anchor.try_resolve(final_html, anchor)
            before = before_node.outer_text(original_html) if before_node else None
            after = after_node.outer_text(final_html) if after_node else None
            label = anchor.get("value")
        else:
            before = full_node_text(original_html, ref)
            after = full_node_text(final_html, ref)
            label = ref
        if before != after:
            raise RebindError(
                f"INTERNAL: frozen node {label!r} changed between template and output "
                f"— the earned-frozen invariant must never be violated"
            )


def _assert_parseable(html_text: str) -> None:
    """Smoke-check the rebound output is still well-formed-enough HTML for html.parser
    to walk without raising. html.parser is deliberately lenient (no nesting/DOCTYPE
    validation) so this catches only gross rebind bugs (e.g. an unbalanced write) — it
    is not a substitute for the real fidelity harness (V1-V6 + period-coherence), which
    is a separate, downstream track."""
    parser = html.parser.HTMLParser()
    try:
        parser.feed(html_text)
        parser.close()
    except Exception as exc:  # pragma: no cover - html.parser rarely raises
        raise RebindError(f"rebound output is not parseable HTML: {exc}") from exc


# ── manifest loading (a pragmatic subset of binding-manifest.schema.json's shape — the ──
# ── fields this engine actually consumes; full JSON-Schema validation would need a ──
# ── third-party lib, which the stdlib-only constraint forbids) ──


def load_manifest(path: Path) -> dict:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RebindError(f"manifest is not valid JSON: {exc}") from exc

    for key in ("manifest_version", "rsg_schema_version", "template_id", "format", "bindings"):
        if key not in manifest:
            raise RebindError(f"manifest missing required field {key!r} (binding-manifest.schema.json)")
    if manifest["format"] != "html":
        raise RebindError(
            f"manifest format is {manifest['format']!r}; rebind-html only applies 'html' manifests"
        )
    if not isinstance(manifest["bindings"], list):
        raise RebindError("manifest 'bindings' must be an array")

    for binding in manifest["bindings"]:
        for key in ("node_id", "anchor", "class", "confidence", "provenance", "data_query"):
            if key not in binding:
                raise RebindError(f"binding {binding.get('node_id', '?')!r} missing required field {key!r}")
        if binding["class"] not in VALID_CLASSES:
            raise RebindError(f"binding {binding['node_id']!r} has unknown class {binding['class']!r}")
        anchor = binding["anchor"]
        if not isinstance(anchor, dict) or "kind" not in anchor or "value" not in anchor:
            raise RebindError(f"binding {binding['node_id']!r} has a malformed anchor (needs kind+value)")
        if binding["class"] == "frozen" and binding["data_query"] is not None:
            raise RebindError(
                f"binding {binding['node_id']!r} is class 'frozen' but carries a data_query "
                f"(schema violation — frozen carries none)"
            )
        if binding["class"] != "frozen" and binding["data_query"] is None:
            raise RebindError(
                f"binding {binding['node_id']!r} is class {binding['class']!r} but carries no "
                f"data_query (schema violation)"
            )

    return manifest


_OLD_CLIENT_COMMENT_MARKER = re.compile(r'old_\w+\s*:\s*"[^"]+"')
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_CDATA_SPAN = re.compile(r"<(script|style)\b[^>]*>.*?</\1>", re.DOTALL | re.IGNORECASE)


def _strip_old_client_comments(html_text: str) -> str:
    """Pre-emit purge (spec §6.6, P0 #1a): remove any HTML comment carrying an old-client TAINT
    block — an `old_*: "..."` line, the exact block the fidelity harness's V4 taint-derivation
    reads. Such a comment is an authoring artifact from the OLD client's template; leaving it in the
    OUTPUT is a hidden-channel leak (the decoded-container tree-walk excludes comments, and V4's
    raw-byte backstop over the full delivered bytes would — correctly — FAIL on it). Only comments
    that actually carry an old-client literal are removed; ordinary comments are preserved."""
    # P3 (round-2): scope the strip to comments OUTSIDE <script>/<style> CDATA, so a legacy
    # <!-- --> inside a script/style body is never touched (can't leak, but don't corrupt CDATA).
    cdata_spans = [mm.span() for mm in _CDATA_SPAN.finditer(html_text)]

    def _drop(m: re.Match) -> str:
        pos = m.start()
        if any(a <= pos < b for a, b in cdata_spans):
            return m.group(0)
        return "" if _OLD_CLIENT_COMMENT_MARKER.search(m.group(0)) else m.group(0)
    return _HTML_COMMENT.sub(_drop, html_text)


def rebind(template_html: str, manifest: dict, new_data) -> tuple[str, list, int]:
    """The engine's pure core: apply every binding in `manifest` to a COPY of
    `template_html` (the caller's `template_html` string is never mutated — Python
    strings are immutable, and every helper above returns a fresh string). Returns
    (output_html, changes, needs_review_count)."""
    # Pre-emit purge FIRST (P0 #1a): strip old-client TAINT comments from the working copy so no
    # old-client identity/value literal survives into the output via a comment channel. The frozen
    # byte-identity proof runs against this purged baseline, so a frozen node bracketing a purged
    # comment still reads as byte-stable (comments are data-free chrome, never a bound value).
    purged_template = _strip_old_client_comments(template_html)
    html_text = purged_template
    changes = []
    needs_review_count = 0
    for binding in manifest["bindings"]:
        html_text = apply_binding(html_text, binding, new_data, changes)
        if binding["class"] == "needs-review":
            needs_review_count += 1
    _assert_frozen_unchanged(purged_template, html_text, manifest["bindings"])
    _assert_parseable(html_text)
    return html_text, changes, needs_review_count


# ── CLI ──


def _emit_error(message: str) -> None:
    print(json.dumps({"schema": SCHEMA, "ok": False, "error": message}), file=sys.stdout)
    print(f"[error] {message}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rebind_html.py",
        description="Apply a Binding Manifest to a COPY of an HTML template and emit "
                    "the regenerated HTML (report-regeneration pipeline stage 3).",
    )
    p.add_argument("--template", required=True, metavar="PATH", help="template HTML, relative path")
    p.add_argument("--manifest", required=True, metavar="PATH", help="binding manifest JSON, relative path")
    p.add_argument("--new-data", required=True, dest="new_data", metavar="PATH",
                   help="resolved new-source data JSON, relative path")
    p.add_argument("--out", required=True, metavar="PATH", help="output HTML path, relative path")
    p.add_argument("--pretty", action="store_true", help="pretty-print the JSON change-manifest")
    return p


def main(argv: list) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        template_path = _guard_path(args.template, must_exist=True)
        manifest_path = _guard_path(args.manifest, must_exist=True)
        data_path = _guard_path(args.new_data, must_exist=True)
        out_path = _guard_path(args.out, must_exist=False)
        if out_path == template_path:
            raise RebindError(
                "--out must not be the same path as --template — rebind-html works on a "
                "COPY; the template is never mutated"
            )
    except RebindError as exc:
        _emit_error(str(exc))
        return 2

    try:
        template_html = template_path.read_text(encoding="utf-8")
        manifest = load_manifest(manifest_path)
        new_data = json.loads(data_path.read_text(encoding="utf-8"))
    except (RebindError, json.JSONDecodeError, OSError) as exc:
        _emit_error(str(exc))
        return 2

    try:
        output_html, changes, needs_review_count = rebind(template_html, manifest, new_data)
    except RebindError as exc:
        _emit_error(str(exc))
        return 2

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output_html, encoding="utf-8")

    payload = {
        "schema": SCHEMA,
        "ok": True,
        "template": args.template,
        "manifest": args.manifest,
        "new_data": args.new_data,
        "output": args.out,
        "template_id": manifest["template_id"],
        "manifest_version": manifest["manifest_version"],
        "binding_count": len(manifest["bindings"]),
        "needs_review_count": needs_review_count,
        "jinja2_available": jinja2 is not None,
        "changes": changes,
    }
    print(json.dumps(payload, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
