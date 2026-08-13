#!/usr/bin/env python3
"""wireframe_lint.py — the mechanically-gated primitives behind the /wireframe skill.

The /wireframe skill has the *executing Claude* author the high-fidelity HTML
Artifact free-hand (a deterministic script cannot produce a comp — FORGE critic
CE-1). That runtime output is behavioral and never reaches CI (`.ravenclaude/runs/`
is gitignored). What CAN be enforced — and is, by audit-gates.sh Gate 145 over
committed fixtures — lives here, stdlib-only (NO jsonschema; mirrors the
extract_brand.py precedent):

  1. a hand-rolled structural VALIDATOR of a wireframe model against
     schemas/wireframe-model.schema.json (kept in sync by hand);
  2. context-aware SANITIZERS the skill requires the HTML author to route every
     brand-color / URI / user-text / flow-label value through:
       - html_text   : HTML-entity escape (text context)
       - css_value   : allowlist -> validated #hex / rgb()/hsl() / keyword only
                       (blocks url() external-fetch + CSP break)
       - uri_scheme  : allowlist http/https/mailto/tel (blocks javascript:/data:)
       - mermaid_label: safe, quoted Mermaid label (RT-3);
       - ascii_text  : single-line, control-free label for the v1.1 ASCII renderer;
  3. DETERMINISTIC emitters — a Mermaid `flowchart` for `flow`-type models (emit_mermaid) and a
     Mermaid nav-map for v1.1 multi-screen (v2) models (emit_screen_flow).

Also validates the v1.1 multi-screen (v2) shape: `screens[]` (mutually exclusive with top-level
`regions`) + optional `flow_edges[]`, with `meta.model_version` widened to "1" | "2".

CLI:
  --self-test              run the bundled contract checks; exit 0 iff all pass.
  --validate FILE          validate a model JSON file; print errors; exit 0/1.
  --emit-mermaid FILE      emit a Mermaid flowchart from a `flow` model to stdout.
  --emit-screen-flow FILE  emit a Mermaid nav-map from a v2 (screens + flow_edges) model.
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# ── vocabulary (kept in sync with schemas/wireframe-model.schema.json) ──────────
META_TYPES = {"page", "app-screen", "dashboard", "flow"}
VIEWPORTS = {"desktop", "mobile", "tablet", "responsive"}
THEMES = {"auto", "light", "dark"}
FIDELITIES = {"high", "structural"}
EMPHASES = {"primary", "secondary", "tertiary"}
REGION_ROLES = {
    "header",
    "nav",
    "sidebar",
    "main",
    "aside",
    "footer",
    "hero",
    "toolbar",
    "filter-bar",
    "canvas",
    "card-grid",
    "modal",
}
REGION_LAYOUTS = {"stack", "row", "columns", "grid", "split"}
SLOT_KINDS = {"text", "image-box", "data-shape"}
COMPONENT_TYPES = {
    "button",
    "input",
    "form",
    "card",
    "table",
    "chart",
    "kpi-stat",
    "list",
    "tabs",
    "breadcrumb",
    "search",
    "avatar",
    "badge",
    "toggle",
    "stepper",
    "nav-item",
    "node",
    "edge",
}
COMPONENT_PROP_KEYS = {
    "label",
    "placeholder_text",
    "variant",
    "state",
    "size",
    "icon",
    "to",
    "id",
    "href",
}
MERMAID_RESERVED = {"end", "graph", "subgraph", "class", "click", "style", "linkStyle"}


# ── validator ───────────────────────────────────────────────────────────────
def _err(errors: list[str], path: str, msg: str) -> None:
    errors.append(f"{path}: {msg}")


def validate_model(model: object) -> list[str]:
    """Return a list of error strings; empty means the model is valid."""
    errors: list[str] = []
    if not isinstance(model, dict):
        return ["<root>: model must be a JSON object"]

    extra = set(model) - {"meta", "regions", "screens", "flow_edges", "$schema"}
    if extra:
        _err(errors, "<root>", f"unknown keys: {sorted(extra)}")
    if "meta" not in model:
        _err(errors, "<root>", "missing required 'meta'")
    # v1 uses top-level `regions`; v2 uses `screens` (+ optional `flow_edges`). They are
    # mutually exclusive so the renderer never has to guess which shape to read (T8).
    has_regions = "regions" in model
    has_screens = "screens" in model
    if has_regions and has_screens:
        _err(errors, "<root>", "'regions' (v1) and 'screens' (v2) are mutually exclusive")
    elif not has_regions and not has_screens:
        _err(errors, "<root>", "missing required 'regions' (v1) or 'screens' (v2)")
    if "flow_edges" in model and not has_screens:
        _err(errors, "<root>", "'flow_edges' requires 'screens' (multi-screen navigation)")

    meta = model.get("meta")
    if isinstance(meta, dict):
        if not isinstance(meta.get("title"), str) or not meta.get("title", "").strip():
            _err(errors, "meta.title", "required non-empty string")
        if meta.get("type") not in META_TYPES:
            _err(errors, "meta.type", f"required, one of {sorted(META_TYPES)}")
        _enum_if_present(errors, "meta.viewport", meta.get("viewport"), VIEWPORTS)
        _enum_if_present(errors, "meta.theme", meta.get("theme"), THEMES)
        _enum_if_present(errors, "meta.fidelity", meta.get("fidelity"), FIDELITIES)
        if "model_version" in meta and meta["model_version"] not in ("1", "2"):
            _err(errors, "meta.model_version", 'must be "1" (regions) or "2" (screens)')
        meta_extra = set(meta) - {
            "title",
            "type",
            "viewport",
            "theme",
            "fidelity",
            "model_version",
            "brand",
        }
        if meta_extra:
            _err(errors, "meta", f"unknown keys: {sorted(meta_extra)}")
    elif meta is not None:
        _err(errors, "meta", "must be an object")

    regions = model.get("regions")
    if isinstance(regions, list):
        if not regions:
            _err(errors, "regions", "must have at least one region")
        for i, region in enumerate(regions):
            _validate_region(errors, f"regions[{i}]", region)
    elif regions is not None:
        _err(errors, "regions", "must be an array")

    screens = model.get("screens")
    if isinstance(screens, list):
        if not screens:
            _err(errors, "screens", "must have at least one screen")
        for i, screen in enumerate(screens):
            _validate_screen(errors, f"screens[{i}]", screen)
    elif screens is not None:
        _err(errors, "screens", "must be an array")

    flow_edges = model.get("flow_edges")
    if isinstance(flow_edges, list):
        for i, edge in enumerate(flow_edges):
            _validate_flow_edge(errors, f"flow_edges[{i}]", edge)
    elif flow_edges is not None:
        _err(errors, "flow_edges", "must be an array")

    return errors


def _validate_screen(errors: list[str], path: str, screen: object) -> None:
    if not isinstance(screen, dict):
        _err(errors, path, "must be an object")
        return
    if not isinstance(screen.get("id"), str) or not screen.get("id", "").strip():
        _err(errors, f"{path}.id", "required non-empty string (a stable screen id)")
    regions = screen.get("regions")
    if isinstance(regions, list):
        if not regions:
            _err(errors, f"{path}.regions", "must have at least one region")
        for i, region in enumerate(regions):
            _validate_region(errors, f"{path}.regions[{i}]", region)
    else:
        _err(errors, f"{path}.regions", "required array")
    extra = set(screen) - {"id", "title", "regions"}
    if extra:
        _err(errors, path, f"unknown keys: {sorted(extra)}")


def _validate_flow_edge(errors: list[str], path: str, edge: object) -> None:
    if not isinstance(edge, dict):
        _err(errors, path, "must be an object")
        return
    for key in ("from", "to"):
        if not isinstance(edge.get(key), str) or not edge.get(key, "").strip():
            _err(errors, f"{path}.{key}", "required non-empty string (a screen id)")
    extra = set(edge) - {"from", "to", "label"}
    if extra:
        _err(errors, path, f"unknown keys: {sorted(extra)}")


def _enum_if_present(errors, path, value, allowed) -> None:
    if value is not None and value not in allowed:
        _err(errors, path, f"must be one of {sorted(allowed)}")


def _validate_region(errors: list[str], path: str, region: object) -> None:
    if not isinstance(region, dict):
        _err(errors, path, "must be an object")
        return
    if region.get("role") not in REGION_ROLES:
        _err(errors, f"{path}.role", f"required, one of {sorted(REGION_ROLES)}")
    _enum_if_present(errors, f"{path}.layout", region.get("layout"), REGION_LAYOUTS)
    _enum_if_present(errors, f"{path}.emphasis", region.get("emphasis"), EMPHASES)
    sections = region.get("sections")
    if isinstance(sections, list):
        if not sections:
            _err(errors, f"{path}.sections", "must have at least one section")
        for i, section in enumerate(sections):
            _validate_section(errors, f"{path}.sections[{i}]", section)
    else:
        _err(errors, f"{path}.sections", "required array")
    extra = set(region) - {"role", "layout", "layout_detail", "emphasis", "sections"}
    if extra:
        _err(errors, path, f"unknown keys: {sorted(extra)}")


def _validate_section(errors: list[str], path: str, section: object) -> None:
    if not isinstance(section, dict):
        _err(errors, path, "must be an object")
        return
    if not isinstance(section.get("kind"), str) or not section.get("kind", "").strip():
        _err(errors, f"{path}.kind", "required non-empty string")
    _enum_if_present(errors, f"{path}.emphasis", section.get("emphasis"), EMPHASES)
    for i, slot in enumerate(section.get("content_slots", []) or []):
        if not isinstance(slot, dict) or slot.get("slot") not in SLOT_KINDS:
            _err(errors, f"{path}.content_slots[{i}].slot", f"one of {sorted(SLOT_KINDS)}")
    for i, comp in enumerate(section.get("components", []) or []):
        _validate_component(errors, f"{path}.components[{i}]", comp)
    extra = set(section) - {"kind", "heading", "emphasis", "content_slots", "components"}
    if extra:
        _err(errors, path, f"unknown keys: {sorted(extra)}")


def _validate_component(errors: list[str], path: str, comp: object) -> None:
    if not isinstance(comp, dict):
        _err(errors, path, "must be an object")
        return
    if comp.get("type") not in COMPONENT_TYPES:
        _err(errors, f"{path}.type", f"required, one of {sorted(COMPONENT_TYPES)}")
    props = comp.get("props")
    if props is not None:
        if not isinstance(props, dict):
            _err(errors, f"{path}.props", "must be an object")
        else:
            extra = set(props) - COMPONENT_PROP_KEYS
            if extra:
                _err(errors, f"{path}.props", f"unknown keys: {sorted(extra)}")


# ── context-aware sanitizers ──────────────────────────────────────────────────
_HTML_ESCAPES = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}
_HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
_FUNC_COLOR_RE = re.compile(r"^(?:rgb|rgba|hsl|hsla)\([0-9.,%\s/]+\)$")
_KEYWORD_RE = re.compile(r"^[a-zA-Z][a-zA-Z-]{0,31}$")
_ALLOWED_URI_SCHEMES = ("http://", "https://", "mailto:", "tel:")


def html_text(s: str) -> str:
    """Escape the five HTML metacharacters for a text/attribute context."""
    return "".join(_HTML_ESCAPES.get(c, c) for c in str(s))


def css_value(s: str) -> str | None:
    """Return the value iff it is a safe CSS color, else None.

    Allows #hex, rgb()/rgba()/hsl()/hsla(), or a plain keyword. Rejects anything
    that could carry url(), a declaration break (`;`/`}`), or a comment — which is
    how a raw brand color reaching <style> becomes an external fetch / CSP break.
    """
    v = str(s).strip()
    if _HEX_RE.match(v) or _FUNC_COLOR_RE.match(v) or _KEYWORD_RE.match(v):
        return v
    return None


def uri_scheme(s: str) -> str | None:
    """Return the URI iff its scheme is allowlisted (or it is relative/anchor)."""
    v = str(s).strip()
    low = v.lower()
    if low.startswith(("javascript:", "data:", "vbscript:", "file:")):
        return None
    if low.startswith(_ALLOWED_URI_SCHEMES):
        return v
    # relative path, anchor, or query — no scheme, so no scheme-based injection
    if v.startswith(("/", "#", "?", "./", "../")) or ":" not in v.split("/", 1)[0]:
        return v
    return None


def mermaid_label(s: str) -> str:
    """Produce a safe, double-quoted-content Mermaid label.

    Mermaid node syntax is `id["label"]`; inside the quotes a literal `"` breaks
    out, and the parser is sensitive to `[](){};` and newlines. We entity-escape
    `"` and `#`, collapse newlines, and strip the structural metacharacters, so a
    hostile label like `A[evil](x)-->B "boom"; end` cannot restructure the graph.
    Reserved words are safe once quoted, so no separate refusal is needed.
    """
    v = str(s).replace("#", "#35;").replace('"', "#quot;")
    v = re.sub(r"[\r\n]+", " ", v)
    v = re.sub(r"[\[\]{}();]", "", v)
    v = v.replace("-->", "→").replace("--", "—")
    return v.strip()


def ascii_text(s: str) -> str:
    """Single-line, control-free label for the ASCII renderer.

    Strips C0 controls and collapses ALL whitespace (incl. newlines/tabs) to single spaces so
    a label can never break the character-grid row structure. It deliberately does NOT strip the
    frame glyphs ``- | +``: those are legitimate content (a KPI ``-12%``, a range ``A - B``), and
    stripping ``-`` would invert ``-12%`` into ``12%`` (RT-4). Border-forgery is instead prevented
    by the renderer CLIPPING every label to its cell interior width — a glyph inside a cell can
    never extend the frame drawn at fixed columns.
    """
    text = re.sub(r"[\x00-\x1f\x7f]+", " ", str(s))
    return re.sub(r"\s+", " ", text).strip()


def _mermaid_id(raw: str) -> str:
    """A safe Mermaid node id: alnum + underscore, never a reserved word."""
    ident = re.sub(r"[^A-Za-z0-9_]", "_", str(raw)).strip("_") or "n"
    if ident in MERMAID_RESERVED or ident[0].isdigit():
        ident = "n_" + ident
    return ident


def emit_mermaid(model: dict) -> str:
    """Deterministic `flowchart TD` from a flow model's node/edge components.

    Walks regions -> sections -> components in document order (no sorting, no
    timestamps, no locale formatting — cross-platform-determinism clean).
    """
    node_lines: list[str] = []
    edge_lines: list[str] = []
    for region in model.get("regions", []) or []:
        for section in region.get("sections", []) or []:
            comps = section.get("components", []) or []
            section_node_id = None
            for c in comps:
                if c.get("type") == "node":
                    props = c.get("props", {}) or {}
                    nid = _mermaid_id(props.get("id") or props.get("label") or "node")
                    label = mermaid_label(props.get("label") or nid)
                    section_node_id = section_node_id or nid
                    node_lines.append(f'    {nid}["{label}"]')
            for c in comps:
                if c.get("type") == "edge":
                    props = c.get("props", {}) or {}
                    frm = _mermaid_id(props.get("id")) if props.get("id") else section_node_id
                    to = _mermaid_id(props.get("to")) if props.get("to") else None
                    if not frm or not to:
                        continue
                    elabel = props.get("label")
                    if elabel:
                        edge_lines.append(f'    {frm} -->|"{mermaid_label(elabel)}"| {to}')
                    else:
                        edge_lines.append(f"    {frm} --> {to}")
    return "\n".join(["flowchart TD", *node_lines, *edge_lines]) + "\n"


def emit_screen_flow(model: dict) -> str:
    """Deterministic Mermaid nav-map (`flowchart LR`) from a v2 model's screens + flow_edges.

    Distinct from emit_mermaid (which renders a `flow`-TYPE model's node/edge components, and
    whose CLI path guards `meta.type == 'flow'` — so it cannot render a multi-screen page/app
    model, the reuse trap RT/CE-2 flagged). This renders the SCREEN-to-SCREEN navigation of a
    multi-screen (v2) model: each screen id is a node, each flow_edge an edge. Labels routed
    through mermaid_label; document order, no sorting/timestamps (cross-platform-determinism).
    """
    node_lines: list[str] = []
    edge_lines: list[str] = []
    seen: list[str] = []
    for scr in model.get("screens", []) or []:
        if not isinstance(scr, dict):
            continue
        sid = _mermaid_id(scr.get("id") or "screen")
        if sid in seen:
            continue
        seen.append(sid)
        label = mermaid_label(scr.get("title") or scr.get("id") or sid)
        node_lines.append(f'    {sid}["{label}"]')
    for edge in model.get("flow_edges", []) or []:
        if not isinstance(edge, dict):
            continue
        frm = _mermaid_id(edge["from"]) if edge.get("from") else None
        to = _mermaid_id(edge["to"]) if edge.get("to") else None
        if not frm or not to:
            continue
        elabel = edge.get("label")
        if elabel:
            edge_lines.append(f'    {frm} -->|"{mermaid_label(elabel)}"| {to}')
        else:
            edge_lines.append(f"    {frm} --> {to}")
    return "\n".join(["flowchart LR", *node_lines, *edge_lines]) + "\n"


# ── bundled self-test (self-contained; matches forge-route.py --self-test) ─────
_GOOD_MODEL = {
    "meta": {"title": "Acme Plumbing", "type": "page", "viewport": "responsive"},
    "regions": [
        {
            "role": "hero",
            "emphasis": "primary",
            "sections": [
                {
                    "kind": "value-prop",
                    "heading": "Fast, honest plumbing",
                    "content_slots": [{"slot": "text", "text": "24/7 emergency callouts"}],
                    "components": [{"type": "button", "props": {"label": "Book now"}}],
                }
            ],
        }
    ],
}
_BAD_MODELS = [
    ({"regions": []}, "missing meta + empty regions"),
    ({"meta": {"title": "X"}, "regions": [{"role": "hero", "sections": []}]}, "missing meta.type"),
    (
        {
            "meta": {"title": "X", "type": "page"},
            "regions": [{"role": "nope", "sections": [{"kind": "k"}]}],
        },
        "bad region role",
    ),
    (
        {
            "meta": {"title": "X", "type": "page"},
            "regions": [
                {"role": "main", "sections": [{"kind": "k", "components": [{"type": "gizmo"}]}]}
            ],
        },
        "unknown component type",
    ),
]
_FLOW_MODEL = {
    "meta": {"title": "Checkout flow", "type": "flow"},
    "regions": [
        {
            "role": "canvas",
            "sections": [
                {
                    "kind": "step",
                    "components": [
                        {"type": "node", "props": {"id": "cart", "label": "View cart"}},
                        {"type": "edge", "props": {"to": "pay", "label": "checkout"}},
                    ],
                },
                {
                    "kind": "step",
                    "components": [{"type": "node", "props": {"id": "pay", "label": "Payment"}}],
                },
            ],
        }
    ],
}
_EXPECTED_MMD = (
    'flowchart TD\n    cart["View cart"]\n    pay["Payment"]\n    cart -->|"checkout"| pay\n'
)


def _self_test() -> int:
    failures: list[str] = []

    if validate_model(_GOOD_MODEL):
        failures.append(f"good model rejected: {validate_model(_GOOD_MODEL)}")
    for model, why in _BAD_MODELS:
        if not validate_model(model):
            failures.append(f"bad model NOT rejected ({why})")

    # sanitizers — malicious input must be neutralized
    if css_value("red;}body{background:url(https://evil/x)}") is not None:
        failures.append("css_value accepted a url()/declaration-break payload")
    if css_value("#0a2540") != "#0a2540":
        failures.append("css_value rejected a valid hex")
    if css_value("rebeccapurple") != "rebeccapurple":
        failures.append("css_value rejected a keyword color")
    for bad in ("javascript:alert(1)", "data:text/html,<script>", "vbscript:x"):
        if uri_scheme(bad) is not None:
            failures.append(f"uri_scheme accepted {bad!r}")
    for ok in ("https://example.com", "mailto:a@b.com", "/relative", "#anchor"):
        if uri_scheme(ok) != ok:
            failures.append(f"uri_scheme rejected {ok!r}")
    if "&lt;script&gt;" not in html_text("<script>"):
        failures.append("html_text did not escape <script>")
    label = mermaid_label('A[evil](x)-->B "boom"; end')
    if any(ch in label for ch in "[]();") or '"' in label or "-->" in label:
        failures.append(f"mermaid_label left a metacharacter: {label!r}")

    # deterministic Mermaid emit
    got = emit_mermaid(_FLOW_MODEL)
    if got != _EXPECTED_MMD:
        failures.append(f"mermaid emit drift:\n--- got ---\n{got}\n--- want ---\n{_EXPECTED_MMD}")
    if emit_mermaid(_FLOW_MODEL) != got:
        failures.append("mermaid emit is non-deterministic")

    # ascii_text (RT-4): strips controls/newlines but PRESERVES structural glyphs
    if ascii_text("-12%") != "-12%":
        failures.append("ascii_text stripped a legitimate '-' (RT-4 regression)")
    if ascii_text("a\nb\tc\x00d") != "a b c d":
        failures.append("ascii_text did not collapse control/newline chars")

    # v2 multi-screen validation
    good_v2 = {
        "meta": {"title": "App", "type": "app-screen", "model_version": "2"},
        "screens": [
            {"id": "home", "regions": [{"role": "main", "sections": [{"kind": "k"}]}]},
            {"id": "detail", "regions": [{"role": "main", "sections": [{"kind": "k"}]}]},
        ],
        "flow_edges": [{"from": "home", "to": "detail", "label": "open"}],
    }
    if validate_model(good_v2):
        failures.append(f"good v2 model rejected: {validate_model(good_v2)}")
    if not validate_model({**good_v2, "regions": [{"role": "main", "sections": [{"kind": "k"}]}]}):
        failures.append("regions+screens (mutually exclusive) NOT rejected")
    if not validate_model({"meta": {"title": "x", "type": "page"}, "flow_edges": []}):
        failures.append("flow_edges without screens NOT rejected")
    bad_edge = {**good_v2, "flow_edges": [{"from": "home"}]}
    if not validate_model(bad_edge):
        failures.append("flow_edge missing 'to' NOT rejected")

    # deterministic screen-flow emit
    sf = emit_screen_flow(good_v2)
    if emit_screen_flow(good_v2) != sf:
        failures.append("emit_screen_flow is non-deterministic")
    if "flowchart LR" not in sf or 'home["home"]' not in sf or "home -->" not in sf:
        failures.append(f"emit_screen_flow output malformed:\n{sf}")

    if failures:
        print("wireframe_lint --self-test: FAIL")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("wireframe_lint --self-test: OK (validator + sanitizers + deterministic Mermaid)")
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────────
def _load(path: str) -> object:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Wireframe model validator + sanitizers + Mermaid emitter."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true", help="run bundled contract checks")
    group.add_argument("--validate", metavar="FILE", help="validate a model JSON file")
    group.add_argument(
        "--emit-mermaid", metavar="FILE", help="emit a Mermaid flowchart from a flow model"
    )
    group.add_argument(
        "--emit-screen-flow",
        metavar="FILE",
        help="emit a Mermaid nav-map from a v2 (screens + flow_edges) model",
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    if args.validate:
        try:
            model = _load(args.validate)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"could not read model: {exc}", file=sys.stderr)
            return 1
        errors = validate_model(model)
        if errors:
            print(f"INVALID ({len(errors)} error(s)):", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)
            return 1
        print("valid")
        return 0

    if args.emit_mermaid:
        try:
            model = _load(args.emit_mermaid)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"could not read model: {exc}", file=sys.stderr)
            return 1
        errors = validate_model(model)
        if errors:
            print("refusing to emit Mermaid from an invalid model", file=sys.stderr)
            return 1
        if model.get("meta", {}).get("type") != "flow":
            print("emit-mermaid expects a meta.type == 'flow' model", file=sys.stderr)
            return 1
        sys.stdout.write(emit_mermaid(model))
        return 0

    if args.emit_screen_flow:
        try:
            model = _load(args.emit_screen_flow)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"could not read model: {exc}", file=sys.stderr)
            return 1
        errors = validate_model(model)
        if errors:
            print("refusing to emit a screen-flow from an invalid model", file=sys.stderr)
            return 1
        if not isinstance(model.get("screens"), list):
            print("emit-screen-flow expects a v2 model with a 'screens' array", file=sys.stderr)
            return 1
        sys.stdout.write(emit_screen_flow(model))
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
