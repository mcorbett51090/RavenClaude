#!/usr/bin/env python3
"""apply_schema.py — the design-clone apply path: a validated design-schema in, sanitized
design tokens + fixed-structure component scaffolds out, wearing the TARGET's brand.

CLONE THE CRAFT, SWAP THE IDENTITY. This path reproduces the reference's *functional
craft* — spacing scale, type scale, grid, elevation ramp, component recipes — while the
identity (logo, signature color, mascot) is structurally unable to leak into the output.

TWO LAYERS OF IDENTITY DEFENCE:

  1. HARD STRUCTURAL NO-READ INVARIANT (the real defence). `apply()` reads only the
     reference's structural geometry (spacing/type_scale/grid/elevation/components) and
     the TARGET brand kit's colors/fonts. Its body does not read the reference's `logos[]`
     or `colors.palette` — even when handed a reference bundle that carries those keys — so
     a reference logo or primary color has no structural route to the output regardless of
     whether the advisory flag fired. `_reference_colors_never_read()` is the anchor for
     that invariant (see its docstring); Gate 194's must-fail mutant proves it has teeth.

  2. IDENTITY-COLOR RE-ENTRY NEUTRALIZATION. A signature color can still try to ride in
     through an elevation/border color component. `_neutralize_shadow()` emits GEOMETRY
     ONLY and replaces any chromatic (identity-bearing) color with a target-owned token
     (`var(--brand-shadow-color)`); a neutral elevation tint (black/gray, achromatic)
     survives verbatim. So `0 0 12px #e10098` → `0 0 12px var(--brand-shadow-color)`,
     while `0 2px 8px rgba(0,0,0,0.1)` survives byte-for-byte.

  3. ADVISORY FLAG (`flag_identity_risks`). A second, never-authoritative layer: it flags
     every logo, every high-frequency saturated reference color (not just role==primary —
     the role guess mislabels signature colors), mascot/illustration keyword hits, and any
     embedded color matching the reference palette. `action` is always "human-decision";
     it never auto-approves; distinctiveness / trade-dress / legal calls route to
     ravenclaude-core/security-reviewer. NOT legal advice.

STATELESS-LOOP BOUNDARY. This is a single, stateless apply pass. ONE PASS IS NOT
CONVERGENCE — patience across iterations is the AGENT's cross-iteration job, never state
held here. The determinate gate is the only stopping proof.

CLI:
  apply_schema.py <ref-design-schema.json> --target-brand <target-brand-kit.json> --out <dir>
  apply_schema.py --self-test        # embedded fixtures; drives Gate 194 (bidirectional)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

from sanitizers import (
    css_length,
    css_number,
    css_shadow,
    css_value,
    split_top_level,
)

# ── color analysis (identity vs elevation-neutral) ────────────────────────────
_HEX_FULL_RE = re.compile(r"^#([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})(?:[0-9a-fA-F]{2})?$")
_HEX_SHORT_RE = re.compile(r"^#([0-9a-fA-F])([0-9a-fA-F])([0-9a-fA-F])(?:[0-9a-fA-F])?$")
_RGB_FN_RE = re.compile(r"^rgba?\(([^()]*)\)$", re.IGNORECASE)
# A color LITERAL anywhere in a string (for scanning shadows/recipes). Linear.
_COLOR_LITERAL_RE = re.compile(
    r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b|(?:rgb|rgba|hsl|hsla)\([^()]*\)",
    re.IGNORECASE,
)
_MASCOT_RE = re.compile(r"\b(mascot|illustration|character|avatar|cartoon|figure)\b", re.IGNORECASE)

_ACHROMATIC_TOL = 16
_NEUTRAL_KEYWORDS = {
    "black",
    "white",
    "transparent",
    "gray",
    "grey",
    "silver",
    "gainsboro",
    "dimgray",
    "dimgrey",
    "lightgray",
    "lightgrey",
    "darkgray",
    "darkgrey",
    "whitesmoke",
    "currentcolor",
}
_IDENTITY_ACTIONS = ("swap", "omit", "human-decision")


def _color_rgb(color: str) -> tuple[int, int, int] | None:
    """Return (r, g, b) 0-255 for a hex or rgb()/rgba() color, or None if not parseable
    (a keyword or an hsl() we deliberately do not decode)."""
    c = str(color).strip()
    m = _HEX_FULL_RE.match(c)
    if m:
        return (int(m.group(1), 16), int(m.group(2), 16), int(m.group(3), 16))
    m = _HEX_SHORT_RE.match(c)
    if m:
        return tuple(int(g * 2, 16) for g in m.groups())  # type: ignore[return-value]
    m = _RGB_FN_RE.match(c)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        if len(parts) < 3:
            return None
        vals: list[int] = []
        for p in parts[:3]:
            try:
                if p.endswith("%"):
                    vals.append(round(float(p[:-1]) * 255 / 100))
                else:
                    vals.append(int(float(p)))
            except ValueError:
                return None
        return (vals[0], vals[1], vals[2])
    return None


def _color_is_neutral(color: str) -> bool:
    """True iff `color` is an elevation-neutral tint (achromatic gray/black/white/transparent)
    that carries no identity. A chromatic hue, or any color we cannot prove achromatic (a bare
    non-neutral keyword, an hsl()), returns False → the apply path replaces it with a
    target-owned token so a reference signature color cannot ride in."""
    kw = str(color).strip().lower()
    if kw in _NEUTRAL_KEYWORDS:
        return True
    rgb = _color_rgb(color)
    if rgb is None:
        return False
    r, g, b = rgb
    return (max(r, g, b) - min(r, g, b)) <= _ACHROMATIC_TOL


def _shadow_token_color(tok: str) -> str | None:
    """Return `tok` iff it is a shadow COLOR token (a css_value match that is neither a
    css_length nor the literal `inset`), else None — so geometry and `inset` are never
    mistaken for a color to neutralize."""
    t = tok.strip()
    if t.lower() == "inset":
        return None
    if css_length(t) is not None:
        return None
    if css_value(t) is not None:
        return t
    return None


# ── the hard no-read invariant anchor ─────────────────────────────────────────
def _reference_colors_never_read(design_schema: dict) -> list:
    """HARD NO-READ INVARIANT anchor. The intent of this path is that apply() does not read
    the reference's `colors.palette` or `logos[]`; this function's body is `return []`, so a
    reference primary color or logo has no route to the generated CSS through it — whether or
    not the advisory flag fired, and whether or not the reference bundle carries those keys.

    ⛔ Do NOT 'implement' this to read `design_schema["colors"]` / `["logos"]` — that would be
    the vulnerability this whole path exists to close. Gate 194's must-fail mutant rewrites
    this body to return the reference palette and checks that the reference-color assertion
    then fails (the assertion's teeth). `design_schema` is accepted only to make that mutant
    a one-line edit; it is intentionally unused here."""
    _ = design_schema
    return []


# ── target brand tokens (the ONLY identity that reaches output) ───────────────
def _as_list(v: object) -> list:
    return v if isinstance(v, list) else []


def _css_font_safe(name: str | None) -> str:
    """Strip characters that would let a font-family name break out of a double-quoted CSS
    custom-property declaration (mirrors extract_brand.py's _css_font_safe)."""
    if not name:
        return "system-ui"
    cleaned = re.sub(r'[";{}()\r\n]', "", str(name)).strip()
    return cleaned or "system-ui"


def _target_tokens(target_brand_kit: dict) -> dict:
    """Resolve the TARGET brand kit's colors/fonts — sanitized (the target kit is untrusted
    too). These are the only colors/fonts emitted; the reference's are never read."""
    tbk = target_brand_kit or {}
    colors = tbk.get("colors") if isinstance(tbk.get("colors"), dict) else {}
    palette = _as_list(colors.get("palette"))

    def role(want: str, fallback: str) -> str:
        for c in palette:
            if isinstance(c, dict) and c.get("role") == want:
                san = css_value(str(c.get("value", "")))
                if san:
                    return san
        return fallback

    def first_color(fallback: str) -> str:
        for c in palette:
            if isinstance(c, dict):
                san = css_value(str(c.get("value", "")))
                if san:
                    return san
        return fallback

    primary = role("primary", "") or first_color("#2563eb")
    typography = tbk.get("typography") if isinstance(tbk.get("typography"), dict) else {}
    fonts = _as_list(typography.get("font_families"))

    def font_by_role(want: str) -> str | None:
        for f in fonts:
            if isinstance(f, dict) and f.get("role") == want:
                return f.get("family")
        return None

    heading = _css_font_safe(font_by_role("heading") or (fonts[0].get("family") if fonts else None))
    body = _css_font_safe(font_by_role("body") or heading)
    return {
        "primary": primary,
        "accent": role("accent", primary),
        "bg": role("background", "#ffffff"),
        "text": role("text", "#1a1a1a"),
        "heading": heading,
        "body": body,
        # A target-owned neutral elevation tint; the token every neutralized shadow color
        # points at. Deliberately NOT any reference value.
        "shadow_color": "rgba(0, 0, 0, 0.15)",
    }


# ── shadow / geometry emission ────────────────────────────────────────────────
def _neutralize_shadow(raw: str, shadow_token: str) -> str | None:
    """Return a geometry-only shadow with any chromatic (identity-bearing) color replaced
    by `shadow_token`, or None if the WHOLE value is unsafe (dropped entirely — never a
    partial salvage). A neutral tint (achromatic) layer survives byte-verbatim."""
    if css_shadow(raw) is None:
        return None
    layers = split_top_level(raw, ",")
    if layers is None:  # css_shadow already guaranteed balanced; defensive
        return None
    out: list[str] = []
    for layer in layers:
        layer = layer.strip()
        toks_raw = split_top_level(layer, " ") or []
        toks = [t.strip() for t in toks_raw if t.strip()]
        chromatic = [t for t in toks if _shadow_token_color(t) and not _color_is_neutral(t)]
        if not chromatic:
            out.append(layer)  # verbatim — a legit neutral shadow is unchanged
            continue
        rebuilt = [
            shadow_token if (_shadow_token_color(t) and not _color_is_neutral(t)) else t
            for t in toks
        ]
        out.append(" ".join(rebuilt))
    return ", ".join(out)


def _length_from(raw: object) -> str | None:
    """Sanitize a spacing/type/grid value to a safe CSS length. A bare number is formatted
    as px (a design-schema spacing/size is a px number); a string is validated as-is."""
    if isinstance(raw, bool):
        return None
    if isinstance(raw, (int, float)):
        n: object = int(raw) if float(raw).is_integer() else raw
        return css_length(f"{n}px")
    if isinstance(raw, str):
        return css_length(raw)
    return None


# ── fixed-structure component scaffolds (value-only; no reference-derived selector) ──
_COMPONENT_ARCHETYPES: dict[str, str] = {
    "button": (
        ".dc-button{padding:var(--space-1, 8px) var(--space-2, 16px);"
        "border-radius:var(--space-1, 8px);background:var(--brand-primary);"
        "color:var(--brand-bg);font-family:var(--brand-font-body);"
        "font-size:var(--font-size-1, 16px);box-shadow:var(--shadow-0, none);border:0}"
    ),
    "card": (
        ".dc-card{padding:var(--space-2, 16px);border-radius:var(--space-1, 8px);"
        "background:var(--brand-bg);color:var(--brand-text);"
        "font-family:var(--brand-font-body);box-shadow:var(--shadow-1, none)}"
    ),
    "nav": (
        ".dc-nav{display:flex;gap:var(--space-2, 16px);padding:var(--space-1, 8px);"
        "background:var(--brand-bg);font-family:var(--brand-font-heading)}"
    ),
    "input": (
        ".dc-input{padding:var(--space-1, 8px);border-radius:var(--space-1, 8px);"
        "font-family:var(--brand-font-body);font-size:var(--font-size-1, 16px);"
        "color:var(--brand-text);background:var(--brand-bg)}"
    ),
}
# The visible content string is OURS — never a reference-derived `content:` / selector.
_COMPONENT_MARKUP: dict[str, str] = {
    "button": '<button class="dc-button">Button</button>',
    "card": '<article class="dc-card"><h3>Card title</h3><p>Card body.</p></article>',
    "nav": '<nav class="dc-nav"><a href="#">Home</a><a href="#">About</a></nav>',
    "input": '<input class="dc-input" type="text" placeholder="Type here" />',
}


def _component_scaffold(name: object) -> dict | None:
    """Return a FIXED-STRUCTURE HTML scaffold for a recognized component archetype, or None
    for anything unrecognized. The reference-derived `name` is matched against a closed
    allowlist and NEVER interpolated raw into markup, a selector, or a property name."""
    if not isinstance(name, str):
        return None
    slug = name.strip().lower()
    css = _COMPONENT_ARCHETYPES.get(slug)
    markup = _COMPONENT_MARKUP.get(slug)
    if css is None or markup is None:
        return None
    html = (
        '<!doctype html>\n<html lang="en">\n<head><meta charset="utf-8" />\n'
        '<link rel="stylesheet" href="design-schema.css" />\n'
        f"<style>\n{css}\n</style>\n</head>\n<body>\n{markup}\n</body>\n</html>\n"
    )
    return {"slug": slug, "html": html}


def _short(v: object, n: int = 80) -> str:
    s = str(v)
    return s if len(s) <= n else s[:n] + "…"


# ── the apply engine ──────────────────────────────────────────────────────────
def apply(design_schema: dict, target_brand_kit: dict, out_dir: str) -> dict:
    """Emit `design-schema.css` (sanitized structural tokens in the TARGET's brand) plus a
    fixed-structure HTML scaffold per recognized component, into `out_dir`. Returns a report
    dict. The hard no-read invariant holds: the reference's `logos[]`/`colors.palette` are
    never read, and an identity color cannot ride in through a shadow/border."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ds = design_schema if isinstance(design_schema, dict) else {}
    target = _target_tokens(target_brand_kit if isinstance(target_brand_kit, dict) else {})

    dropped: list[dict] = []
    emitted = {"space": 0, "font_size": 0, "grid": 0, "shadow": 0, "component": 0}

    lines = [
        "/* design-schema.css — generated by the design-clone apply path.",
        " * Craft cloned from the reference; identity is the TARGET's own. Do not hand-edit.",
        " */",
        ":root {",
        f"  --brand-primary: {target['primary']};",
        f"  --brand-accent: {target['accent']};",
        f"  --brand-bg: {target['bg']};",
        f"  --brand-text: {target['text']};",
        f"  --brand-shadow-color: {target['shadow_color']};",
        f'  --brand-font-heading: "{target["heading"]}", system-ui, sans-serif;',
        f'  --brand-font-body: "{target["body"]}", system-ui, sans-serif;',
    ]

    # HARD NO-READ INVARIANT: this loop body does not run on the real impl (the anchor returns
    # an empty list). A mutant that makes it read the reference palette leaks a reference color
    # → Gate 194 red. See _reference_colors_never_read.
    for idx, leaked in enumerate(_reference_colors_never_read(ds)):
        lines.append(f"  --ref-color-{idx}: {leaked};")

    # spacing scale → --space-*
    spacing = ds.get("spacing") if isinstance(ds.get("spacing"), dict) else {}
    for i, raw in enumerate(_as_list(spacing.get("scale"))):
        val = _length_from(raw)
        if val is None:
            dropped.append({"where": "spacing.scale", "value": _short(raw)})
            continue
        lines.append(f"  --space-{i}: {val};")
        emitted["space"] += 1

    # type scale → --font-size-*
    type_scale = ds.get("type_scale") if isinstance(ds.get("type_scale"), dict) else {}
    for i, raw in enumerate(_as_list(type_scale.get("sizes"))):
        val = _length_from(raw)
        if val is None:
            dropped.append({"where": "type_scale.sizes", "value": _short(raw)})
            continue
        lines.append(f"  --font-size-{i}: {val};")
        emitted["font_size"] += 1

    # grid → --grid-* / --container-max / --breakpoint-*
    grid = ds.get("grid") if isinstance(ds.get("grid"), dict) else {}
    container_max = _length_from(grid.get("container_max")) if grid.get("container_max") else None
    if container_max is not None:
        lines.append(f"  --container-max: {container_max};")
        emitted["grid"] += 1
    gutter = _length_from(grid.get("gutter")) if grid.get("gutter") else None
    if gutter is not None:
        lines.append(f"  --grid-gutter: {gutter};")
        emitted["grid"] += 1
    if grid.get("columns") is not None:
        cols = css_number(str(grid.get("columns")))
        if cols is not None:
            lines.append(f"  --grid-columns: {cols};")
            emitted["grid"] += 1
    for i, raw in enumerate(_as_list(grid.get("breakpoints"))):
        val = _length_from(raw)
        if val is None:
            dropped.append({"where": "grid.breakpoints", "value": _short(raw)})
            continue
        lines.append(f"  --breakpoint-{i}: {val};")
        emitted["grid"] += 1

    # elevation → --shadow-* (geometry only; identity color neutralized to a target token)
    elevation = ds.get("elevation") if isinstance(ds.get("elevation"), dict) else {}
    for i, raw in enumerate(_as_list(elevation.get("shadows"))):
        neutralized = _neutralize_shadow(str(raw), "var(--brand-shadow-color)")
        if neutralized is None:
            dropped.append({"where": "elevation.shadows", "value": _short(raw)})
            continue
        lines.append(f"  --shadow-{i}: {neutralized};")
        emitted["shadow"] += 1

    lines.append("}")
    (out / "design-schema.css").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # component scaffolds — fixed structure, value-only
    components_written: list[str] = []
    for comp in _as_list(ds.get("components")):
        name = comp.get("name") if isinstance(comp, dict) else None
        scaffold = _component_scaffold(name)
        if scaffold is None:
            continue
        fname = f"component-{scaffold['slug']}.html"
        (out / fname).write_text(scaffold["html"], encoding="utf-8")
        components_written.append(fname)
        emitted["component"] += 1

    report = {
        "out_dir": str(out),
        "css": "design-schema.css",
        "components": components_written,
        "emitted": emitted,
        "dropped": dropped,
        "notes": [
            "clone the craft, swap the identity: colors/fonts are the TARGET's; the "
            "reference's logos[]/colors.palette were never read.",
            "one pass is not convergence — patience across iterations is the agent's job.",
        ],
    }
    (out / "apply-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return report


# ── advisory identity-risk flag (never authoritative) ─────────────────────────
def _colors_in(text: str) -> list[str]:
    return [m.group(0) for m in _COLOR_LITERAL_RE.finditer(str(text))]


def _scan_embedded_colors(design_schema: dict) -> list[str]:
    """Every color literal embedded in elevation shadows or component recipes — the re-entry
    surface a signature color can hide in."""
    found: list[str] = []
    elevation = (
        design_schema.get("elevation") if isinstance(design_schema.get("elevation"), dict) else {}
    )
    for raw in _as_list(elevation.get("shadows")):
        found.extend(_colors_in(str(raw)))
    for comp in _as_list(design_schema.get("components")):
        if isinstance(comp, dict) and isinstance(comp.get("recipe"), dict):
            for v in comp["recipe"].values():
                found.extend(_colors_in(str(v)))
    return found


def flag_identity_risks(reference_brand_kit: dict, reference_design_schema: dict) -> list[dict]:
    """Advisory — NEVER authoritative. Flags every logo, every high-frequency saturated
    reference color (not just role==primary — the role guess mislabels signature colors),
    mascot/illustration keyword hits, and any color embedded in elevation/components. Every
    flag's `action` is 'human-decision'; this never auto-approves. Distinctiveness /
    trade-dress / legal calls route to ravenclaude-core/security-reviewer. NOT legal advice.

    The hard no-read invariant in apply() is the real defence; this is the second layer, and
    it fires even when a heuristic here misses (nothing here gates the apply path)."""
    flags: list[dict] = []
    rbk = reference_brand_kit if isinstance(reference_brand_kit, dict) else {}
    rds = reference_design_schema if isinstance(reference_design_schema, dict) else {}

    # 1) every non-empty logos[] entry + a mascot/illustration keyword scan on it
    for lg in _as_list(rbk.get("logos")):
        if not isinstance(lg, dict):
            continue
        ev = lg.get("role") or lg.get("src") or lg.get("alt") or "logo asset"
        flags.append(
            {
                "kind": "logo",
                "evidence": f"reference logo present ({_short(str(ev))}) — never carry it over",
                "action": "human-decision",
            }
        )
        hay = " ".join(str(lg.get(k, "")) for k in ("role", "src", "alt", "context")).lower()
        if _MASCOT_RE.search(hay):
            flags.append(
                {
                    "kind": "mascot",
                    "evidence": f"mascot/illustration keyword in reference logo ({_short(hay)})",
                    "action": "human-decision",
                }
            )

    # 2) every saturated reference color — not only role==primary
    colors = rbk.get("colors") if isinstance(rbk.get("colors"), dict) else {}
    ref_palette_colors: set[str] = set()
    for c in _as_list(colors.get("palette")):
        if not isinstance(c, dict):
            continue
        san = css_value(str(c.get("value", "")))
        if san and not _color_is_neutral(san):
            ref_palette_colors.add(san.lower())
            flags.append(
                {
                    "kind": "saturated-color",
                    "evidence": (
                        f"high-frequency saturated reference color {san} "
                        f"(role guess {c.get('role', 'unknown')!r} is NOT trusted)"
                    ),
                    "action": "human-decision",
                }
            )

    # 3) illustration/mascot keyword hits across component names + anatomy
    for comp in _as_list(rds.get("components")):
        if not isinstance(comp, dict):
            continue
        hay = (
            str(comp.get("name", "")) + " " + " ".join(str(a) for a in _as_list(comp.get("anatomy")))
        ).lower()
        if _MASCOT_RE.search(hay):
            flags.append(
                {
                    "kind": "illustration",
                    "evidence": f"mascot/illustration keyword in a component ({_short(hay)})",
                    "action": "human-decision",
                }
            )

    # 4) any color embedded in elevation/components (re-entry surface), flagged when chromatic
    for col in _scan_embedded_colors(rds):
        if _color_is_neutral(col):
            continue
        matches = " (matches reference palette)" if col.lower() in ref_palette_colors else ""
        flags.append(
            {
                "kind": "shadow-embedded-color",
                "evidence": f"chromatic color {col} embedded in elevation/components{matches}",
                "action": "human-decision",
            }
        )
    return flags


# ── embedded fixtures + self-test (self-contained; drives Gate 194) ───────────
_TARGET_BRAND_KIT = {
    "colors": {
        "palette": [
            {"value": "#0055ff", "role": "primary"},
            {"value": "#ffffff", "role": "background"},
            {"value": "#0b1020", "role": "text"},
            {"value": "#00c2a8", "role": "accent"},
        ]
    },
    "typography": {
        "font_families": [
            {"family": "Inter", "role": "heading"},
            {"family": "Georgia", "role": "body"},
        ]
    },
}

_REFERENCE_SIGNATURE_COLOR = "#e10098"  # the reference's magenta — must never reach output

_LEGIT_VALUES = {
    "source": {"url": "https://ref.example", "fetched_at": "2026-08-13T00:00:00Z"},
    "capture_method": "static",
    "spacing": {"base_unit": 8, "scale": [8, 16, 24], "capture_method": "static"},
    "type_scale": {"base_size": 16, "ratio": 1.25, "sizes": [16, 20], "capture_method": "static"},
    "grid": {
        "breakpoints": ["768px"],
        "columns": 12,
        "gutter": "1.5rem",
        "container_max": "1200px",
        "capture_method": "static",
    },
    "elevation": {"shadows": ["0 2px 8px rgba(0,0,0,0.1)"], "capture_method": "static"},
    "components": [{"name": "button"}, {"name": "card"}],
    "identity_flags": [],
    "confidence_notes": [],
}

_HOSTILE_SHADOW = {
    "source": {"url": "https://ref.example", "fetched_at": "2026-08-13T00:00:00Z"},
    "capture_method": "static",
    "spacing": {"base_unit": 8, "scale": [8], "capture_method": "static"},
    "type_scale": {"sizes": [16], "capture_method": "static"},
    "grid": {"breakpoints": [], "capture_method": "static"},
    "elevation": {
        "shadows": ["0 0 10px url(javascript:alert(1))", "8px; background:url(//exfil)"],
        "capture_method": "static",
    },
    "components": [],
    "identity_flags": [],
    "confidence_notes": [],
}

_IDENTITY_COLOR_IN_SHADOW = {
    "source": {"url": "https://ref.example", "fetched_at": "2026-08-13T00:00:00Z"},
    "capture_method": "static",
    "spacing": {"scale": [8], "capture_method": "static"},
    "type_scale": {"sizes": [16], "capture_method": "static"},
    "grid": {"breakpoints": [], "capture_method": "static"},
    "elevation": {"shadows": [f"0 0 12px {_REFERENCE_SIGNATURE_COLOR}"], "capture_method": "static"},
    "components": [],
    # carried so flag_identity_risks can flag the palette AND the "matches palette" embed
    "colors": {"palette": [{"value": _REFERENCE_SIGNATURE_COLOR, "role": "accent"}]},
    "identity_flags": [],
    "confidence_notes": [],
}

# A reference BUNDLE — a design-schema PLUS logos[]/colors.palette. Proves apply() does not
# read those keys even when they are present on the object it is handed.
_REFERENCE_WITH_LOGO_AND_PRIMARY = {
    "source": {"url": "https://ref.example", "fetched_at": "2026-08-13T00:00:00Z"},
    "capture_method": "static",
    "spacing": {"base_unit": 8, "scale": [8, 16], "capture_method": "static"},
    "type_scale": {"sizes": [16, 20], "capture_method": "static"},
    "grid": {"breakpoints": ["768px"], "container_max": "1200px", "capture_method": "static"},
    "elevation": {"shadows": ["0 2px 8px rgba(0,0,0,0.1)"], "capture_method": "static"},
    "components": [{"name": "button"}],
    "colors": {
        "palette": [
            {"value": _REFERENCE_SIGNATURE_COLOR, "role": "primary"},
            {"value": "#00b3a4", "role": "accent"},
        ]
    },
    "logos": [{"role": "header-logo", "src": "https://ref.example/logo.svg", "alt": "Ref mascot"}],
    "identity_flags": [],
    "confidence_notes": [],
}

_IMAGE_EXTS = (".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".avif", ".bmp", ".tiff")


def _self_test() -> int:
    failures: list[str] = []
    root = Path(tempfile.mkdtemp(prefix="design-clone-selftest-"))
    target = _TARGET_BRAND_KIT
    target_primary = "#0055ff"

    # 1) SURVIVE — legit structural values present VERBATIM (the false-negative half: a
    #    drop-everything sanitizer would ship an empty stylesheet and pass a hostile-only gate).
    apply(_LEGIT_VALUES, target, str(root / "legit"))
    legit_css = (root / "legit" / "design-schema.css").read_text(encoding="utf-8")
    for needle in ("8px", "1.5rem", "0 2px 8px rgba(0,0,0,0.1)", "1200px"):
        if needle not in legit_css:
            failures.append(f"SURVIVE: legit value {needle!r} missing from design-schema.css")
    if target_primary not in legit_css:
        failures.append("SURVIVE: target primary color missing (target identity not applied)")

    # 2) NEUTRALIZE — hostile shadows dropped whole (no partial salvage), payloads absent.
    apply(_HOSTILE_SHADOW, target, str(root / "hostile"))
    hostile_css = (root / "hostile" / "design-schema.css").read_text(encoding="utf-8")
    for needle in ("url(", "javascript:", "expression(", "//exfil", "background:"):
        if needle in hostile_css:
            failures.append(f"NEUTRALIZE: hostile payload {needle!r} reached design-schema.css")
    if "--shadow-" in hostile_css:
        failures.append("NEUTRALIZE: a hostile shadow was emitted (partial salvage — must drop whole)")

    # 3a) IDENTITY (re-entry) — a signature color embedded in a shadow is replaced by a
    #     target-owned token, not carried into design-schema.css.
    apply(_IDENTITY_COLOR_IN_SHADOW, target, str(root / "identity"))
    identity_css = (root / "identity" / "design-schema.css").read_text(encoding="utf-8")
    if _REFERENCE_SIGNATURE_COLOR in identity_css:
        failures.append("IDENTITY: reference signature color rode into design-schema.css via a shadow")
    if "var(--brand-shadow-color)" not in identity_css:
        failures.append("IDENTITY: neutralized shadow did not reference the target shadow token")

    # 3b) NO-READ invariant — the reference bundle's logos[]/colors.palette never reach output,
    #     and the output tree carries ZERO logo/image files (structural, not content).
    apply(_REFERENCE_WITH_LOGO_AND_PRIMARY, target, str(root / "bundle"))
    bundle_dir = root / "bundle"
    bundle_css = (bundle_dir / "design-schema.css").read_text(encoding="utf-8")
    for ref_color in (_REFERENCE_SIGNATURE_COLOR, "#00b3a4"):
        if ref_color in bundle_css:
            failures.append(f"NO-READ: reference color {ref_color} reached design-schema.css")
    if target_primary not in bundle_css:
        failures.append("NO-READ: target primary color missing (output must wear the target's brand)")
    image_files = [p.name for p in bundle_dir.rglob("*") if p.suffix.lower() in _IMAGE_EXTS]
    if image_files:
        failures.append(f"IDENTITY(structural): output tree carries logo/image files: {image_files}")

    # 4) FLAG — fires on logo + saturated-color + shadow-embedded-color; never auto-approves.
    bundle_flags = flag_identity_risks(
        _REFERENCE_WITH_LOGO_AND_PRIMARY, _REFERENCE_WITH_LOGO_AND_PRIMARY
    )
    kinds = {f["kind"] for f in bundle_flags}
    if "logo" not in kinds:
        failures.append("FLAG: no logo flag on the logo fixture")
    if "saturated-color" not in kinds:
        failures.append("FLAG: no saturated-color flag on the saturated-color fixture")
    identity_flags = flag_identity_risks(_IDENTITY_COLOR_IN_SHADOW, _IDENTITY_COLOR_IN_SHADOW)
    if "shadow-embedded-color" not in {f["kind"] for f in identity_flags}:
        failures.append("FLAG: no shadow-embedded-color flag on the identity-color-in-shadow fixture")
    for f in bundle_flags + identity_flags:
        if f.get("action") not in _IDENTITY_ACTIONS:
            failures.append(
                f"FLAG: illegal action {f.get('action')!r} (must be human-decision, never auto-approve)"
            )
        if f.get("action") != "human-decision":
            failures.append(f"FLAG: {f.get('kind')} did not route to human-decision (never auto-approve)")

    if failures:
        print("apply_schema --self-test: FAIL")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print(
        "apply_schema --self-test: OK "
        "(SURVIVE verbatim + NEUTRALIZE whole-drop + IDENTITY re-entry + NO-READ structural + FLAG fires)"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Apply a design-schema to a target brand — clone the craft, swap the identity.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("reference", nargs="?", help="reference design-schema.json (the craft to clone)")
    ap.add_argument("--target-brand", help="target brand-kit.json (the identity to apply)")
    ap.add_argument("--out", default="design-clone-out", help="output directory")
    ap.add_argument(
        "--self-test", action="store_true", help="run the embedded fixtures (drives Gate 194)"
    )
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()

    if not args.reference or not args.target_brand:
        ap.error("<reference design-schema.json> and --target-brand are required unless --self-test")

    try:
        design_schema = json.loads(Path(args.reference).read_text(encoding="utf-8"))
        target_brand_kit = json.loads(Path(args.target_brand).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"✗ could not read inputs: {exc}", file=sys.stderr)
        return 1

    report = apply(design_schema, target_brand_kit, args.out)
    # The reference bundle acts as its own brand-kit view for the advisory flag.
    flags = flag_identity_risks(design_schema, design_schema)
    report["identity_flags"] = flags
    (Path(args.out) / "apply-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"✓ applied to {args.out}/ — css: {report['css']}, components: {report['components']}")
    print(f"  emitted: {report['emitted']}  dropped: {len(report['dropped'])}")
    print(f"  identity risk flags (advisory, human-decision): {len(flags)}")
    if flags:
        print("  route distinctiveness / trade-dress / legal to ravenclaude-core/security-reviewer.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
