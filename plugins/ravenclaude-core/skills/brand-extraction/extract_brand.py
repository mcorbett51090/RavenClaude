#!/usr/bin/env python3
"""Brand & logo extraction engine for the brand-extraction skill.

Point it at a website home page and it harvests every logo variant it can find
plus the brand "schema" (design tokens — colors, typography, radii) and emits a
ready-to-apply brand kit:

    brand-kit/
      logos/              downloaded logo assets (every variant found)
      brand.json          the schema (validated by schemas/brand-kit.schema.json)
      brand.css           CSS custom properties ready to <link> or paste
      report-template.html a starter report wired to brand.css + the logo
      brand-summary.md    human-readable summary + confidence notes

Stdlib only (urllib + html.parser + re) — no third-party dependencies, matching
the marketplace's no-new-deps discipline. Every network operation degrades
gracefully: a failed fetch is recorded in confidence_notes, never a crash.

Usage:
    python3 extract_brand.py <url> [--out DIR] [--max-stylesheets N]
                                   [--no-download] [--timeout SECONDS]

The heuristics (which color is "primary", which font is "heading") are best-guess
and labelled as such in brand.json `confidence_notes` and per-item `source`
fields — a human picks the final tokens from the ranked candidates.
"""

from __future__ import annotations

import argparse
import base64
import datetime as _dt
import json
import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

_UA = "Mozilla/5.0 (compatible; RavenClaude-brand-extraction/1.0; +brand-kit)"
_DEFAULT_TIMEOUT = 20
_MAX_ASSET_BYTES = 6 * 1024 * 1024  # 6 MiB cap per downloaded logo
_MAX_HTML_BYTES = 5 * 1024 * 1024  # 5 MiB cap on the page itself
_MAX_CSS_BYTES = 3 * 1024 * 1024  # 3 MiB cap per stylesheet

# Hex / rgb / hsl color literals in CSS.
_HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
_RGB_RE = re.compile(r"rgba?\(\s*[\d.]+%?\s*,\s*[\d.]+%?\s*,\s*[\d.]+%?\s*(?:,\s*[\d.]+%?\s*)?\)")
_HSL_RE = re.compile(r"hsla?\(\s*[\d.]+\s*,\s*[\d.]+%\s*,\s*[\d.]+%\s*(?:,\s*[\d.]+%?\s*)?\)")
# A CSS custom property declaration: --name: value;
_CUSTOM_PROP_RE = re.compile(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;{}]+)")
_FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;{}]+)", re.IGNORECASE)
_RADIUS_RE = re.compile(r"border-radius\s*:\s*([^;{}]+)", re.IGNORECASE)
_SVG_BLOCK_RE = re.compile(r"<svg\b[^>]*>.*?</svg>", re.IGNORECASE | re.DOTALL)

# Words in a class/id/alt/src that strongly suggest a logo element.
_LOGO_HINT_RE = re.compile(r"\b(logo|brand|wordmark|site-?title|masthead)\b", re.IGNORECASE)

# Color names we treat as "neutral" (background/text candidates, not brand hues).
_NEUTRALS = {
    "#fff",
    "#ffffff",
    "#000",
    "#000000",
    "#fafafa",
    "#f5f5f5",
    "#eeeeee",
    "#cccccc",
    "#999999",
    "#666666",
    "#333333",
    "#111111",
    "#1a1a1a",
    "transparent",
}


# --------------------------------------------------------------------------- #
# Networking (fail-safe)
# --------------------------------------------------------------------------- #


def _fetch(url: str, timeout: int, *, max_bytes: int) -> tuple[bytes | None, str | None, str | None]:
    """Return (body, content_type, error). On any failure body is None and error is set."""
    if url.startswith("data:"):
        try:
            header, _, data = url.partition(",")
            ctype = header[5:].split(";")[0] or "application/octet-stream"
            raw = base64.b64decode(data) if ";base64" in header else data.encode("utf-8")
            return raw[:max_bytes], ctype, None
        except Exception as exc:  # noqa: BLE001 - data URI is best-effort
            return None, None, f"data-uri decode failed: {exc}"
    try:
        req = Request(url, headers={"User-Agent": _UA, "Accept": "*/*"})
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310 - user-supplied public URL
            ctype = resp.headers.get("Content-Type", "")
            body = resp.read(max_bytes + 1)
            if len(body) > max_bytes:
                return None, ctype, f"exceeded {max_bytes} byte cap"
            return body, ctype, None
    except Exception as exc:  # noqa: BLE001 - network errors are expected & recorded
        return None, None, str(exc)


# --------------------------------------------------------------------------- #
# HTML parsing
# --------------------------------------------------------------------------- #


class _BrandParser(HTMLParser):
    """Collects logo-bearing tags and design-token-bearing tags from the page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.icons: list[dict] = []  # <link rel=icon|apple-touch-icon|mask-icon>
        self.metas: dict[str, str] = {}  # og:image, theme-color, etc.
        self.img_logos: list[dict] = []  # <img> that look like logos
        self.stylesheet_hrefs: list[str] = []  # <link rel=stylesheet>
        self.font_links: list[str] = []  # Google-Fonts-style links
        self.inline_styles: list[str] = []  # <style> blocks
        self.style_attrs: list[str] = []  # style="" attribute values
        self.title: str | None = None
        self.picture_sources: list[dict] = []  # <source> inside <picture>
        self._region: list[str] = []  # header/nav/footer nesting stack
        self._in_title = False
        self._in_style = False

    # -- region tracking so we can label header-logo vs footer-logo ---------- #
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag in ("header", "nav", "footer"):
            self._region.append(tag)
        if tag == "title":
            self._in_title = True
        elif tag == "style":
            self._in_style = True
        elif tag == "link":
            self._handle_link(a)
        elif tag == "meta":
            self._handle_meta(a)
        elif tag == "img":
            self._handle_img(a)
        elif tag == "source":
            self._handle_source(a)
        if "style" in a and a["style"].strip():
            self.style_attrs.append(a["style"])

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag in ("header", "nav", "footer") and self._region and self._region[-1] == tag:
            self._region.pop()

    def handle_endtag(self, tag: str) -> None:
        if tag in ("header", "nav", "footer") and self._region and self._region[-1] == tag:
            self._region.pop()
        if tag == "title":
            self._in_title = False
        elif tag == "style":
            self._in_style = False

    def handle_data(self, data: str) -> None:
        if self._in_title and data.strip():
            self.title = (self.title or "") + data.strip()
        elif self._in_style and data.strip():
            self.inline_styles.append(data)

    # -- per-tag handlers --------------------------------------------------- #
    def _handle_link(self, a: dict) -> None:
        rel = a.get("rel", "").lower()
        href = a.get("href", "").strip()
        if not href:
            return
        if "stylesheet" in rel:
            if "fonts.googleapis.com" in href or "fonts.gstatic" in href or "use.typekit" in href:
                self.font_links.append(href)
            else:
                self.stylesheet_hrefs.append(href)
        elif any(k in rel for k in ("icon", "mask-icon", "apple-touch-icon", "shortcut")):
            self.icons.append(
                {
                    "rel": rel,
                    "href": href,
                    "sizes": a.get("sizes", ""),
                    "type": a.get("type", ""),
                    "color": a.get("color", ""),
                }
            )

    def _handle_meta(self, a: dict) -> None:
        key = (a.get("property") or a.get("name") or "").lower()
        content = a.get("content", "").strip()
        if not key or not content:
            return
        if key in ("og:image", "og:image:url", "twitter:image", "theme-color", "og:site_name", "msapplication-tilecolor"):
            self.metas.setdefault(key, content)

    def _handle_img(self, a: dict) -> None:
        src = (a.get("src") or a.get("data-src") or "").strip()
        haystack = " ".join((a.get("class", ""), a.get("id", ""), a.get("alt", ""), src))
        if src and _LOGO_HINT_RE.search(haystack):
            region = self._region[-1] if self._region else "body"
            self.img_logos.append(
                {
                    "src": src,
                    "alt": a.get("alt", ""),
                    "region": region,
                    "width": a.get("width", ""),
                    "height": a.get("height", ""),
                }
            )

    def _handle_source(self, a: dict) -> None:
        srcset = (a.get("srcset") or a.get("src") or "").strip()
        media = a.get("media", "").lower()
        if srcset and ("prefers-color-scheme" in media or _LOGO_HINT_RE.search(srcset)):
            theme = "dark" if "dark" in media else ("light" if "light" in media else "any")
            self.picture_sources.append({"srcset": srcset.split()[0], "theme": theme})


# --------------------------------------------------------------------------- #
# Design-token extraction from CSS text
# --------------------------------------------------------------------------- #


def _normalize_color(value: str) -> str:
    value = value.strip().lower()
    # Expand #abc -> #aabbcc for stable dedupe.
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        value = "#" + "".join(c * 2 for c in value[1:])
    return value


def _is_neutral(color: str) -> bool:
    return _normalize_color(color) in _NEUTRALS


def _collect_colors(css_text: str) -> Counter:
    counts: Counter = Counter()
    for rx in (_HEX_RE, _RGB_RE, _HSL_RE):
        for m in rx.finditer(css_text):
            counts[_normalize_color(m.group(0))] += 1
    return counts


def _collect_custom_properties(css_text: str) -> dict[str, str]:
    props: dict[str, str] = {}
    for name, value in _CUSTOM_PROP_RE.findall(css_text):
        v = value.strip()
        # Only keep the first definition (closest to :root usually wins anyway).
        props.setdefault(name, v)
    return props


def _collect_font_families(css_text: str) -> Counter:
    counts: Counter = Counter()
    for stack in _FONT_FAMILY_RE.findall(css_text):
        first = stack.split(",")[0].strip().strip("'\"")
        if first and not first.startswith("var(") and first.lower() not in ("inherit", "initial", "unset"):
            counts[first] += 1
    return counts


def _collect_radii(css_text: str) -> Counter:
    counts: Counter = Counter()
    for val in _RADIUS_RE.findall(css_text):
        v = val.strip()
        if v and v != "0" and "var(" not in v:
            counts[v.split()[0]] += 1
    return counts


# --------------------------------------------------------------------------- #
# Logo inventory assembly
# --------------------------------------------------------------------------- #


def _ext_from(ctype: str | None, url: str) -> str:
    if ctype:
        ctype = ctype.split(";")[0].strip().lower()
        mapping = {
            "image/svg+xml": "svg",
            "image/png": "png",
            "image/jpeg": "jpg",
            "image/x-icon": "ico",
            "image/vnd.microsoft.icon": "ico",
            "image/webp": "webp",
            "image/gif": "gif",
            "image/avif": "avif",
        }
        if ctype in mapping:
            return mapping[ctype]
    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lstrip(".").lower()
    return ext if ext else "img"


def _build_logo_candidates(parser: _BrandParser, base_url: str, inline_svgs: list[str]) -> list[dict]:
    cands: list[dict] = []

    def add(role: str, src: str, *, context: str = "", theme: str = "any", extra: dict | None = None) -> None:
        item = {"role": role, "src": urljoin(base_url, src), "context": context, "theme": theme}
        if extra:
            item.update(extra)
        cands.append(item)

    for icon in parser.icons:
        rel = icon["rel"]
        if "apple-touch" in rel:
            role = "apple-touch-icon"
        elif "mask-icon" in rel:
            role = "mask-icon"
        else:
            role = "favicon"
        add(role, icon["href"], context=f"rel={rel} sizes={icon['sizes']}", extra={"declared_color": icon.get("color", "")})

    for key, role in (("og:image", "og-image"), ("twitter:image", "twitter-image")):
        if key in parser.metas:
            add(role, parser.metas[key], context=f"meta {key}")

    for img in parser.img_logos:
        role = "header-logo" if img["region"] in ("header", "nav") else ("footer-logo" if img["region"] == "footer" else "body-logo")
        add(role, img["src"], context=f"<img> in <{img['region']}> alt={img['alt']!r}", extra={"width": img["width"], "height": img["height"]})

    for src in parser.picture_sources:
        add("picture-source", src["srcset"], context="<picture><source>", theme=src["theme"])

    # Inline SVGs found in the header/nav region are stored as text (no URL to fetch).
    for i, svg in enumerate(inline_svgs):
        cands.append(
            {
                "role": "inline-svg",
                "src": None,
                "context": "inline <svg> in header/nav",
                "theme": "any",
                "svg_markup": svg,
                "_inline_index": i,
            }
        )

    # Dedupe by resolved src, keeping the first (most specific) role.
    seen: set[str] = set()
    deduped: list[dict] = []
    for c in cands:
        key = c.get("src") or f"inline-{c.get('_inline_index')}"
        if key in seen:
            continue
        seen.add(key)
        deduped.append(c)
    return deduped


# --------------------------------------------------------------------------- #
# Output writers
# --------------------------------------------------------------------------- #


def _rank_palette(color_counts: Counter, theme_color: str | None, custom_props: dict[str, str]) -> list[dict]:
    palette: list[dict] = []
    used: set[str] = set()

    # 1. Named custom properties whose value is a color — the most reliable signal.
    for name, value in custom_props.items():
        cval = None
        for rx in (_HEX_RE, _RGB_RE, _HSL_RE):
            m = rx.search(value)
            if m:
                cval = _normalize_color(m.group(0))
                break
        if not cval or cval in used:
            continue
        lname = name.lower()
        # Check accent/secondary before primary/brand so "--brand-accent" -> accent,
        # not primary (a name can contain both "brand" and "accent").
        if "accent" in lname:
            role = "accent"
        elif "secondary" in lname:
            role = "secondary"
        elif "primary" in lname or "brand" in lname:
            role = "primary"
        elif "bg" in lname or "background" in lname or "surface" in lname:
            role = "background"
        elif "text" in lname or "ink" in lname or "fg" in lname or "foreground" in lname:
            role = "text"
        else:
            role = "unknown"
        palette.append({"value": cval, "role": role, "source": "css-custom-property", "name": name})
        used.add(cval)

    # 2. theme-color meta.
    if theme_color:
        tc = _normalize_color(theme_color)
        if tc not in used:
            palette.append({"value": tc, "role": "primary", "source": "theme-color-meta", "name": "theme-color"})
            used.add(tc)

    # 3. Frequency-ranked saturated colors as additional candidates.
    for color, count in color_counts.most_common():
        if color in used or _is_neutral(color):
            continue
        palette.append({"value": color, "role": "unknown", "source": "frequency", "count": count})
        used.add(color)
        if len(palette) >= 24:
            break
    return palette


_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.DOTALL)


def _font_roles_from_selectors(css_text: str) -> tuple[str | None, str | None]:
    """Best-guess (heading_family, body_family) from selector context.

    A font-family declared on an h1/h2/h3 selector is almost certainly the heading
    face; one declared on `body`/`html` is the body face. More reliable than raw
    frequency, which can't tell heading from body.
    """
    heading = body = None
    for selector, decls in _RULE_RE.findall(css_text):
        m = _FONT_FAMILY_RE.search(decls)
        if not m:
            continue
        fam = m.group(1).split(",")[0].strip().strip("'\"")
        if not fam or fam.startswith("var("):
            continue
        sel = selector.lower()
        if heading is None and re.search(r"\bh[1-3]\b", sel):
            heading = fam
        if body is None and re.search(r"(^|[,\s])(body|html)\b", sel):
            body = fam
    return heading, body


def _rank_fonts(font_counts: Counter, font_links: list[str], css_text: str) -> tuple[list[dict], list[str]]:
    google_families: list[str] = []
    for href in font_links:
        for fam in re.findall(r"family=([^&:]+)", href):
            google_families.append(fam.replace("+", " ").split(":")[0])

    heading_fam, body_fam = _font_roles_from_selectors(css_text)
    fonts: list[dict] = []
    seen: set[str] = set()
    # Frequency order, but role is decided by selector context when known.
    for fam, _ in font_counts.most_common():
        if fam.lower() in seen:
            continue
        seen.add(fam.lower())
        if heading_fam and fam.lower() == heading_fam.lower():
            role = "heading"
        elif body_fam and fam.lower() == body_fam.lower():
            role = "body"
        else:
            role = "unknown"
        fonts.append({"family": fam, "source": "font-family", "count": font_counts[fam], "role": role})
    # If selector context gave us nothing, fall back to frequency order (1st=heading, 2nd=body).
    if heading_fam is None and body_fam is None and len(fonts) >= 1:
        fonts[0]["role"] = "heading"
        if len(fonts) >= 2:
            fonts[1]["role"] = "body"
    for fam in google_families:
        if fam.lower() not in seen:
            seen.add(fam.lower())
            fonts.append({"family": fam, "source": "google-fonts", "role": "unknown"})
    return fonts, sorted(set(google_families))


def _primary_color(palette: list[dict]) -> str:
    for c in palette:
        if c["role"] == "primary":
            return c["value"]
    for c in palette:
        if c["role"] in ("accent", "secondary"):
            return c["value"]
    return palette[0]["value"] if palette else "#2563eb"


def _role_color(palette: list[dict], role: str, fallback: str) -> str:
    for c in palette:
        if c["role"] == role:
            return c["value"]
    return fallback


def _write_brand_css(brand: dict, path: str) -> None:
    palette = brand["colors"]["palette"]
    primary = _primary_color(palette)
    bg = _role_color(palette, "background", "#ffffff")
    text = _role_color(palette, "text", "#1a1a1a")
    accent = _role_color(palette, "accent", primary)
    fonts = brand["typography"]["font_families"]
    heading_font = next((f["family"] for f in fonts if f["role"] == "heading"), fonts[0]["family"] if fonts else "system-ui")
    body_font = next((f["family"] for f in fonts if f["role"] == "body"), heading_font)
    radius = brand["radii"][0] if brand["radii"] else "8px"

    lines = [
        "/* Brand kit — generated by the brand-extraction skill.",
        f" * Source: {brand['source']['url']}",
        f" * Generated: {brand['source']['fetched_at']}",
        " * Heuristic tokens — review brand-summary.md before shipping. */",
        ":root {",
        f"  --brand-primary: {primary};",
        f"  --brand-accent: {accent};",
        f"  --brand-bg: {bg};",
        f"  --brand-text: {text};",
        f"  --brand-radius: {radius};",
        f'  --brand-font-heading: "{heading_font}", system-ui, sans-serif;',
        f'  --brand-font-body: "{body_font}", system-ui, sans-serif;',
    ]
    # Pass through every named custom property we found, verbatim, for fidelity —
    # but never one that collides with our reserved --brand-* synthetic tokens
    # (the source token's value already informed the synthetic one above).
    reserved = {
        "--brand-primary",
        "--brand-accent",
        "--brand-bg",
        "--brand-text",
        "--brand-radius",
        "--brand-font-heading",
        "--brand-font-body",
    }
    for name, value in brand["colors"]["custom_properties"].items():
        if name in reserved:
            continue
        lines.append(f"  {name}: {value};")
    lines.append("}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def _write_report_template(brand: dict, path: str, logo_rel: str | None) -> None:
    title = brand["source"].get("site_name") or brand["source"].get("title") or "Report"
    logo_html = (
        f'<img src="{logo_rel}" alt="{title} logo" class="brand-logo" />'
        if logo_rel
        else f'<span class="brand-wordmark">{title}</span>'
    )
    html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title} — Report</title>
    <link rel="stylesheet" href="brand.css" />
    <style>
      body {{
        margin: 0;
        font-family: var(--brand-font-body);
        color: var(--brand-text);
        background: var(--brand-bg);
        line-height: 1.6;
      }}
      header.brand-header {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1.25rem 2rem;
        border-bottom: 3px solid var(--brand-primary);
      }}
      .brand-logo {{ height: 40px; width: auto; }}
      .brand-wordmark {{ font-family: var(--brand-font-heading); font-size: 1.5rem; font-weight: 700; color: var(--brand-primary); }}
      main {{ max-width: 60rem; margin: 0 auto; padding: 2rem; }}
      h1, h2, h3 {{ font-family: var(--brand-font-heading); color: var(--brand-primary); }}
      a {{ color: var(--brand-accent); }}
      .brand-card {{
        border: 1px solid color-mix(in srgb, var(--brand-text) 12%, transparent);
        border-radius: var(--brand-radius);
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
      }}
      .brand-accent-bar {{ height: 4px; background: var(--brand-accent); border-radius: var(--brand-radius); }}
    </style>
  </head>
  <body>
    <header class="brand-header">
      {logo_html}
      <strong>{title}</strong>
    </header>
    <main>
      <h1>Report title</h1>
      <p>Replace this body with your generated report content. The colors, fonts,
        and logo above are pulled from <code>{brand['source']['url']}</code>.</p>
      <div class="brand-card">
        <h2>Section</h2>
        <p>Cards, headings, and links inherit the brand tokens automatically.</p>
      </div>
      <div class="brand-accent-bar"></div>
    </main>
  </body>
</html>
"""
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)


def _write_summary(brand: dict, path: str) -> None:
    palette = brand["colors"]["palette"]
    fonts = brand["typography"]["font_families"]
    logos = brand["logos"]
    lines = [
        f"# Brand kit — {brand['source'].get('site_name') or brand['source'].get('title') or brand['source']['url']}",
        "",
        f"- **Source:** {brand['source']['url']}",
        f"- **Fetched:** {brand['source']['fetched_at']}",
        f"- **Page title:** {brand['source'].get('title') or '(none)'}",
        "",
        "## Logos found",
        "",
    ]
    if logos:
        lines.append("| Role | Source | Local file | Theme |")
        lines.append("|---|---|---|---|")
        for lg in logos:
            src = lg.get("src") or "(inline svg)"
            local = lg.get("local_path") or ("logos/" + lg["role"] + ".svg" if lg.get("svg_markup") else "—")
            lines.append(f"| {lg['role']} | {src} | {local} | {lg.get('theme', 'any')} |")
    else:
        lines.append("_No logo candidates were found — check the page manually._")
    lines += ["", "## Colors (ranked candidates)", ""]
    if palette:
        lines.append("| Value | Role (guess) | Source | Name/Count |")
        lines.append("|---|---|---|---|")
        for c in palette[:16]:
            meta = c.get("name") or (f"x{c['count']}" if c.get("count") else "")
            lines.append(f"| `{c['value']}` | {c['role']} | {c['source']} | {meta} |")
    else:
        lines.append("_No colors detected._")
    lines += ["", "## Typography", ""]
    if fonts:
        for f in fonts[:8]:
            lines.append(f"- **{f['family']}** — role: {f['role']} (source: {f['source']})")
    else:
        lines.append("_No font families detected._")
    lines += ["", "## Confidence notes", ""]
    for note in brand["confidence_notes"]:
        lines.append(f"- {note}")
    lines += [
        "",
        "## How to use",
        "",
        "1. Review the ranked colors/fonts above and fix any mislabeled roles in `brand.json`.",
        "2. `brand.css` exposes `--brand-primary/-accent/-bg/-text` + every source custom property.",
        "3. `report-template.html` is a working starter — `<link rel=\"stylesheet\" href=\"brand.css\">`"
        " and drop your report content into `<main>`.",
        "4. Logos are in `logos/` — pick the variant (light/dark, raster/svg) your report needs.",
        "",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #


def extract(url: str, out_dir: str, *, max_stylesheets: int, download: bool, timeout: int) -> dict:
    notes: list[str] = []
    if not urlparse(url).scheme:
        url = "https://" + url

    html_bytes, ctype, err = _fetch(url, timeout, max_bytes=_MAX_HTML_BYTES)
    if html_bytes is None:
        raise SystemExit(f"Could not fetch {url}: {err}")
    html_text = html_bytes.decode("utf-8", errors="replace")

    parser = _BrandParser()
    try:
        parser.feed(html_text)
    except Exception as exc:  # noqa: BLE001 - malformed HTML shouldn't abort
        notes.append(f"HTML parse hit an error (continuing with partial data): {exc}")

    # Inline header/nav SVGs (logo-as-svg is common in modern sites).
    inline_svgs: list[str] = []
    header_match = re.search(r"<(header|nav)\b.*?</\1>", html_text, re.IGNORECASE | re.DOTALL)
    search_scope = header_match.group(0) if header_match else html_text[:20000]
    for svg in _SVG_BLOCK_RE.findall(search_scope)[:5]:
        if len(svg) < 60000:  # skip giant illustration SVGs
            inline_svgs.append(svg)

    # Gather CSS text: inline <style>, style attrs, then external stylesheets.
    css_chunks: list[str] = list(parser.inline_styles) + parser.style_attrs
    fetched_sheets = 0
    for href in parser.stylesheet_hrefs:
        if fetched_sheets >= max_stylesheets:
            notes.append(f"Stopped after {max_stylesheets} stylesheets (--max-stylesheets to raise).")
            break
        sheet_url = urljoin(url, href)
        body, _, sheet_err = _fetch(sheet_url, timeout, max_bytes=_MAX_CSS_BYTES)
        if body is None:
            notes.append(f"Stylesheet fetch failed ({sheet_url}): {sheet_err}")
            continue
        css_chunks.append(body.decode("utf-8", errors="replace"))
        fetched_sheets += 1
    css_text = "\n".join(css_chunks)

    color_counts = _collect_colors(css_text)
    custom_props = _collect_custom_properties(css_text)
    # Keep only custom properties whose value contains a color (the brand-relevant ones).
    color_props = {
        n: v for n, v in custom_props.items() if any(rx.search(v) for rx in (_HEX_RE, _RGB_RE, _HSL_RE))
    }
    font_counts = _collect_font_families(css_text)
    radius_counts = _collect_radii(css_text)

    theme_color = parser.metas.get("theme-color") or parser.metas.get("msapplication-tilecolor")
    palette = _rank_palette(color_counts, theme_color, color_props)
    fonts, google_families = _rank_fonts(font_counts, parser.font_links, css_text)
    radii = [r for r, _ in radius_counts.most_common(6)]

    logos = _build_logo_candidates(parser, url, inline_svgs)

    # Build the brand record before downloads so writers can reference it.
    brand: dict = {
        "$schema": "../../../../schemas/brand-kit.schema.json",
        "source": {
            "url": url,
            "fetched_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "title": parser.title,
            "site_name": parser.metas.get("og:site_name"),
        },
        "colors": {
            "theme_color": _normalize_color(theme_color) if theme_color else None,
            "palette": palette,
            "custom_properties": color_props,
        },
        "typography": {
            "font_families": fonts,
            "google_fonts": google_families,
            "font_links": parser.font_links,
        },
        "logos": logos,
        "radii": radii,
        "confidence_notes": notes,
    }

    # Downloads.
    os.makedirs(out_dir, exist_ok=True)
    logos_dir = os.path.join(out_dir, "logos")
    os.makedirs(logos_dir, exist_ok=True)

    if download:
        used_names: set[str] = set()
        for idx, lg in enumerate(logos):
            if lg.get("svg_markup"):
                fname = f"{lg['role']}-{idx}.svg"
                with open(os.path.join(logos_dir, fname), "w", encoding="utf-8") as fh:
                    fh.write(lg["svg_markup"])
                lg["local_path"] = f"logos/{fname}"
                lg["downloaded"] = True
                lg.pop("svg_markup", None)
                continue
            src = lg.get("src")
            if not src:
                continue
            body, asset_ctype, asset_err = _fetch(src, timeout, max_bytes=_MAX_ASSET_BYTES)
            if body is None:
                lg["downloaded"] = False
                lg["error"] = asset_err
                notes.append(f"Logo download failed ({lg['role']} {src}): {asset_err}")
                continue
            ext = _ext_from(asset_ctype, src)
            base = f"{lg['role']}-{idx}.{ext}"
            while base in used_names:
                idx += 1
                base = f"{lg['role']}-{idx}.{ext}"
            used_names.add(base)
            with open(os.path.join(logos_dir, base), "wb") as fh:
                fh.write(body)
            lg["local_path"] = f"logos/{base}"
            lg["format"] = ext
            lg["downloaded"] = True
    else:
        for lg in logos:
            lg.pop("svg_markup", None)
        notes.append("Run without --no-download to fetch the logo asset bytes into logos/.")

    if not palette:
        notes.append("No brand colors detected — the site may load CSS via JS or from blocked origins.")
    if not logos:
        notes.append("No logo candidates detected — inspect the page's header markup manually.")
    if not fonts:
        notes.append("No web fonts detected — the site may use system fonts.")

    # Writers.
    with open(os.path.join(out_dir, "brand.json"), "w", encoding="utf-8") as fh:
        json.dump(brand, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    _write_brand_css(brand, os.path.join(out_dir, "brand.css"))
    primary_logo = next(
        (lg.get("local_path") for lg in logos if lg["role"] in ("header-logo", "inline-svg") and lg.get("local_path")),
        next((lg.get("local_path") for lg in logos if lg.get("local_path")), None),
    )
    _write_report_template(brand, os.path.join(out_dir, "report-template.html"), primary_logo)
    _write_summary(brand, os.path.join(out_dir, "brand-summary.md"))
    return brand


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Extract logos + brand design tokens from a website home page.")
    ap.add_argument("url", help="Home page URL (scheme optional; https assumed).")
    ap.add_argument("--out", default="brand-kit", help="Output directory (default: brand-kit/).")
    ap.add_argument("--max-stylesheets", type=int, default=8, help="Max external stylesheets to fetch (default: 8).")
    ap.add_argument("--no-download", action="store_true", help="Inventory logos without downloading the bytes.")
    ap.add_argument("--timeout", type=int, default=_DEFAULT_TIMEOUT, help=f"Per-request timeout (default: {_DEFAULT_TIMEOUT}s).")
    args = ap.parse_args(argv)

    brand = extract(
        args.url,
        args.out,
        max_stylesheets=args.max_stylesheets,
        download=not args.no_download,
        timeout=args.timeout,
    )
    n_logos = len(brand["logos"])
    n_colors = len(brand["colors"]["palette"])
    n_fonts = len(brand["typography"]["font_families"])
    print(f"Brand kit written to {args.out}/")
    print(f"  logos: {n_logos}   colors: {n_colors}   fonts: {n_fonts}")
    print("  files: brand.json, brand.css, report-template.html, brand-summary.md, logos/")
    if brand["confidence_notes"]:
        print("  notes:")
        for note in brand["confidence_notes"]:
            print(f"    - {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
