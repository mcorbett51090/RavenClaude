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
import html
import ipaddress
import json
import os
import re
import socket
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urljoin, urlparse
from urllib.request import (
    HTTPDefaultErrorHandler,
    HTTPErrorProcessor,
    HTTPHandler,
    HTTPRedirectHandler,
    HTTPSHandler,
    OpenerDirector,
    Request,
)

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
# Networking (fail-safe + SSRF/LFR hardened)  [RT1-#4]
# --------------------------------------------------------------------------- #
#
# A brand-extraction run fetches SUB-RESOURCES (stylesheets, logos) whose URLs come
# from an untrusted reference page. The default urllib opener leaves two holes open:
#   1. Local-file read — the default opener installs FileHandler/FTPHandler, so a
#      hostile `<link href="file:///etc/passwd">` would be READ and its bytes folded
#      into the harvested CSS (and thence a shared brand kit).
#   2. SSRF to internal / cloud-metadata ranges — `http://169.254.169.254/…`,
#      loopback, and RFC-1918 private ranges.
# Defense: an EXPLICIT opener installing ONLY the http(s) handlers (no File/FTP/Unknown),
# a scheme + resolved-host guard that runs BEFORE any socket is opened, and a redirect
# guard that re-validates every hop's scheme AND host and caps the redirect count. The
# existing size cap + timeout already bound bandwidth; the `data:` branch is unchanged.

_ALLOWED_FETCH_SCHEMES = ("http", "https")
_MAX_REDIRECTS = 5


def _host_is_blocked(host: str | None) -> str | None:
    """Return a reason string iff `host` is (or resolves to) a private / loopback /
    link-local / metadata / reserved address, else None. A bare IP literal is checked
    with NO network; a DNS name is resolved and EVERY address it maps to is checked, so
    a name pointing at 127.0.0.1 / 169.254.169.254 is caught too."""
    if not host:
        return "no host in URL"
    host = host.strip("[]")  # unwrap an IPv6 literal
    addrs = set()
    try:
        addrs.add(ipaddress.ip_address(host))
    except ValueError:
        try:
            for info in socket.getaddrinfo(host, None):
                addrs.add(ipaddress.ip_address(info[4][0]))
        except (OSError, ValueError) as exc:
            return f"host {host!r} did not resolve ({exc})"
    if not addrs:
        return f"host {host!r} did not resolve"
    for ip in addrs:
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            return f"host {host!r} resolves to a blocked address ({ip})"
    return None


def _fetch_scheme_host_guard(url: str) -> str | None:
    """Return a refusal reason iff `url` must not be fetched (non-http(s) scheme, or a
    blocked host), else None. Runs BEFORE any connection is opened."""
    parts = urlparse(url)
    scheme = (parts.scheme or "").lower()
    if scheme not in _ALLOWED_FETCH_SCHEMES:
        return f"refused: scheme {scheme or '(none)'!r} is not http(s)"
    reason = _host_is_blocked(parts.hostname)
    if reason:
        return f"refused: {reason}"
    return None


class _GuardedRedirectHandler(HTTPRedirectHandler):
    """Re-validate every redirect hop's scheme AND resolved host, and cap the count —
    a permissive redirect is an SSRF/LFR bypass of the up-front guard."""

    max_redirections = _MAX_REDIRECTS

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        reason = _fetch_scheme_host_guard(newurl)
        if reason is not None:
            raise HTTPError(newurl, code, reason, headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_HTTP_OPENER = None


def _get_http_opener() -> OpenerDirector:
    """An opener installing ONLY the http(s) machinery — no FileHandler / FTPHandler /
    UnknownHandler / DataHandler — so a `file:`/`ftp:` URL cannot be opened even if the
    scheme guard is somehow bypassed (defense in depth). Built once."""
    global _HTTP_OPENER
    if _HTTP_OPENER is None:
        opener = OpenerDirector()
        opener.add_handler(HTTPHandler())
        opener.add_handler(HTTPSHandler())
        opener.add_handler(_GuardedRedirectHandler())
        opener.add_handler(HTTPErrorProcessor())
        opener.add_handler(HTTPDefaultErrorHandler())
        _HTTP_OPENER = opener
    return _HTTP_OPENER


def _fetch(
    url: str, timeout: int, *, max_bytes: int
) -> tuple[bytes | None, str | None, str | None]:
    """Return (body, content_type, error). On any failure body is None and error is set.

    http(s)-only + host-guarded (see the module header): a non-http(s) scheme or a
    private/loopback/link-local/metadata host is refused BEFORE any connection, so a
    hostile sub-resource URL's bytes never enter the harvested CSS or the brand kit.
    """
    if url.startswith("data:"):
        try:
            header, _, data = url.partition(",")
            ctype = header[5:].split(";")[0] or "application/octet-stream"
            raw = base64.b64decode(data) if ";base64" in header else data.encode("utf-8")
            return raw[:max_bytes], ctype, None
        except Exception as exc:  # noqa: BLE001 - data URI is best-effort
            return None, None, f"data-uri decode failed: {exc}"
    _guard_err = _fetch_scheme_host_guard(url)
    if _guard_err is not None:
        return None, None, _guard_err
    try:
        req = Request(url, headers={"User-Agent": _UA, "Accept": "*/*"})
        with _get_http_opener().open(req, timeout=timeout) as resp:
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
        if key in (
            "og:image",
            "og:image:url",
            "twitter:image",
            "theme-color",
            "og:site_name",
            "msapplication-tilecolor",
        ):
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
        if (
            first
            and not first.startswith("var(")
            and first.lower() not in ("inherit", "initial", "unset")
        ):
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
# Design-schema collectors — declared CSS only (the static ceiling)  [P2]
# --------------------------------------------------------------------------- #
#
# Five stdlib collectors + pure derivation fns extend the brand kit with a full DESIGN
# schema (spacing scale, type scale, elevation ramp, grid/breakpoints, component
# recipes) written to design-schema.json and validated by
# plugins/ravenclaude-core/scripts/check-design-schema.py.
# Every value is DECLARED CSS only — a stdlib parser recovers no computed/rendered style
# — so every dimension is stamped capture_method:"static" and degrades HONESTLY
# (base_unit / ratio come back null, with a confidence note, when no clean fit exists).
# Each collector/derivation is independently testable and SORTS before emit (determinism).
# All regexes are LINEAR (negated classes, no nested quantifier) — no catastrophic
# backtracking over a large css_text (ReDoS).

# Declared margin / padding / gap declarations → their raw value strings.
_SPACING_DECL_RE = re.compile(
    r"\b(?:margin|padding|gap|row-gap|column-gap|grid-gap)"
    r"(?:-(?:top|right|bottom|left))?\s*:\s*([^;{}]+)",
    re.IGNORECASE,
)
# A single length token inside a declaration value (px, or rem/em converted to px).
_LEN_TOKEN_RE = re.compile(r"(-?\d*\.?\d+)\s*(px|rem|em)\b", re.IGNORECASE)
_FONT_SIZE_DECL_RE = re.compile(r"font-size\s*:\s*([^;{}]+)", re.IGNORECASE)
_BOX_SHADOW_DECL_RE = re.compile(r"box-shadow\s*:\s*([^;{}]+)", re.IGNORECASE)
_MEDIA_WIDTH_RE = re.compile(r"@media[^{}]*?\(\s*(?:min|max)-width\s*:\s*([^)]+)\)", re.IGNORECASE)
# A container max-width DECLARATION (not a media condition: the negative lookbehind
# refuses a `(` or `-` immediately before, so `(max-width:…)` and `min-width` never match).
_MAX_WIDTH_DECL_RE = re.compile(
    r"(?<![-(])max-width\s*:\s*([0-9.]+(?:px|rem|em|vw|%))", re.IGNORECASE
)
_GRID_COLS_RE = re.compile(r"grid-template-columns\s*:\s*repeat\(\s*(\d+)", re.IGNORECASE)
_PX_PER_REM = 16.0
_SPACING_TOL = 0.15
_RATIO_TOL = 0.06
_TYPE_RATIOS = (1.2, 1.25, 1.333, 1.414, 1.618)


def _round_px(v: float) -> float:
    """Round to ≤2 dp and normalize an integral float to an int so the emitted scale is
    stable/deterministic (8 not 8.000001)."""
    r = round(v, 2)
    return int(r) if r == int(r) else r


def _lengths_to_px(value: str) -> list[float]:
    """Every length token in a declaration value, as px (rem/em → px at 16)."""
    out: list[float] = []
    for num, unit in _LEN_TOKEN_RE.findall(value):
        try:
            n = float(num)
        except ValueError:
            continue
        out.append(n if unit.lower() == "px" else n * _PX_PER_REM)
    return out


def _collect_spacing(css_text: str) -> list[float]:
    """Every declared margin/padding/gap length (px; rem/em → px), positive, distinct."""
    vals: set[float] = set()
    for decl in _SPACING_DECL_RE.findall(css_text):
        for px in _lengths_to_px(decl):
            if px > 0:
                vals.add(_round_px(px))
    return sorted(vals)


def _derive_spacing_scale(values: list[float]) -> tuple[int | None, list[float], str | None]:
    """Fit a base unit — 8 preferred over 4 when BOTH fit within tolerance (an 8-multiple
    set also fits 4, so the larger, more-informative base is tried first). Returns
    (base_unit|None, sorted_scale, confidence_note|None). No fit ⇒ null + a note."""
    scale = sorted(values)
    if not scale:
        return None, scale, "spacing: no declared margin/padding/gap lengths found"
    best_base = None
    for base in (8, 4):
        residual = sum(min(v % base, base - (v % base)) for v in scale) / (len(scale) * base)
        if residual <= _SPACING_TOL and best_base is None:
            best_base = base
    if best_base is None:
        return None, scale, (
            f"spacing.base_unit: no clean 4px/8px base-unit fit for {scale} — carrying the raw scale"
        )
    return best_base, scale, None


def _collect_font_sizes(css_text: str) -> list[float]:
    """Every declared font-size length (px; rem/em → px), positive, distinct."""
    vals: set[float] = set()
    for decl in _FONT_SIZE_DECL_RE.findall(css_text):
        for px in _lengths_to_px(decl):
            if px > 0:
                vals.add(_round_px(px))
    return sorted(vals)


def _derive_type_scale(
    sizes: list[float],
) -> tuple[float | None, float | None, list[float], str | None]:
    """Fit a modular-scale ratio to the sorted distinct sizes. Returns
    (base_size|None, ratio|None, sorted_sizes, confidence_note|None). No ratio within
    tolerance ⇒ ratio null + a note, but the raw sizes are always carried."""
    s = sorted(sizes)
    if not s:
        return None, None, s, "type_scale: no declared font-size lengths found"
    base_size = s[0]
    if len(s) < 2:
        return base_size, None, s, "type_scale.ratio: only one font-size observed — no ratio to fit"
    ratios = [s[i + 1] / s[i] for i in range(len(s) - 1) if s[i] > 0]
    if not ratios:
        return base_size, None, s, "type_scale.ratio: could not compute step ratios"
    best_ratio = None
    best_res = None
    for cand in _TYPE_RATIOS:
        res = sum(abs(r - cand) for r in ratios) / len(ratios)
        if best_res is None or res < best_res:
            best_ratio, best_res = cand, res
    if best_res is None or best_res > _RATIO_TOL:
        closest = f"{best_ratio} at residual {round(best_res, 3)}" if best_res is not None else "n/a"
        return base_size, None, s, (
            f"type_scale.ratio: no modular-scale ratio within tolerance (closest {closest}) "
            "— carrying the raw sizes"
        )
    return base_size, best_ratio, s, None


def _shadow_weight(shadow: str) -> float:
    """Elevation weight of a box-shadow = blur (+ spread) of its FIRST layer, parsed from
    that layer's length tokens (offset-x, offset-y, blur, spread)."""
    lengths = _lengths_to_px(shadow.split(",")[0])
    if len(lengths) >= 4:
        return abs(lengths[2]) + abs(lengths[3])
    if len(lengths) == 3:
        return abs(lengths[2])
    if lengths:
        return abs(lengths[-1])
    return 0.0


def _collect_shadows(css_text: str) -> list[str]:
    """Distinct declared box-shadow values (raw, whitespace-normalized), excluding
    none/0/inherit and var()-referencing forms."""
    seen: set[str] = set()
    out: list[str] = []
    for decl in _BOX_SHADOW_DECL_RE.findall(css_text):
        v = " ".join(decl.split()).strip()
        low = v.lower()
        if not v or low in ("none", "0", "inherit", "initial", "unset") or "var(" in low:
            continue
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _rank_elevation(shadows: list[str]) -> list[str]:
    """Order distinct shadows into an ascending elevation ramp by parsed blur/spread
    (ties broken by the raw string, for determinism)."""
    return sorted(shadows, key=lambda s: (_shadow_weight(s), s))


def _px_of(value: str) -> float:
    """Best-effort numeric px of a raw breakpoint/length string, for sorting."""
    m = _LEN_TOKEN_RE.search(value)
    if m:
        n = float(m.group(1))
        return n if m.group(2).lower() == "px" else n * _PX_PER_REM
    m2 = re.match(r"\s*(-?\d*\.?\d+)", value)
    return float(m2.group(1)) if m2 else 0.0


def _collect_breakpoints(css_text: str) -> list[str]:
    """Declared @media (min/max-width: …) values, distinct, as raw text."""
    seen: set[str] = set()
    out: list[str] = []
    for val in _MEDIA_WIDTH_RE.findall(css_text):
        v = " ".join(val.split()).strip()
        if v and "var(" not in v.lower() and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _derive_grid(css_text: str, breakpoints: list[str]) -> dict:
    """Assemble the grid dimension from declared @media breakpoints + container
    max-width + an optional grid column count. Text only — declared, never computed."""
    bps = sorted(breakpoints, key=_px_of)
    max_widths = [m.strip() for m in _MAX_WIDTH_DECL_RE.findall(css_text) if "var(" not in m.lower()]
    container_max = max(max_widths, key=_px_of) if max_widths else None
    cols_match = _GRID_COLS_RE.search(css_text)
    columns = int(cols_match.group(1)) if cols_match else None
    return {
        "breakpoints": bps,
        "columns": columns,
        "gutter": None,
        "container_max": container_max,
        "capture_method": "static",
    }


_COMPONENT_ARCHETYPES = (
    ("button", ("button", ".btn", ".button")),
    ("card", (".card",)),
    ("nav", ("nav", ".nav", ".navbar")),
    ("input", ("input", ".input", ".form-control", ".field")),
)
_COMPONENT_PROPS = (
    "padding",
    "border-radius",
    "border",
    "box-shadow",
    "background",
    "background-color",
    "color",
    "font-size",
    "font-weight",
    "gap",
    "display",
)


def _selector_matches(selector: str, needles: tuple[str, ...]) -> bool:
    """True iff any comma-separated part of `selector` matches an archetype needle. A
    class needle (".btn") matches as a substring; a bare element needle ("nav") matches
    only as a whole token, never a substring of another word."""
    for part in selector.lower().split(","):
        part = part.strip()
        for needle in needles:
            if needle.startswith("."):
                if needle in part:
                    return True
            elif re.search(r"(^|[\s>+~])" + re.escape(needle) + r"(?![\w-])", part):
                return True
    return False


def _recipe_from_decls(decls: str) -> dict[str, str]:
    """The declared, allow-listed structural properties of a component rule (value text
    only; var()-referencing values are skipped)."""
    recipe: dict[str, str] = {}
    for prop in _COMPONENT_PROPS:
        m = re.search(r"(?:^|[;{]|\s)" + re.escape(prop) + r"\s*:\s*([^;{}]+)", decls, re.IGNORECASE)
        if m:
            val = " ".join(m.group(1).split()).strip()
            if val and "var(" not in val.lower():
                recipe[prop] = val
    return recipe


def _collect_component_hints(css_text: str) -> list[dict]:
    """Recurring button/card/nav/input rules → structural recipes (declared props only).
    First rule per archetype wins (deterministic by document order); the result is sorted
    into the fixed archetype order before emit."""
    found: dict[str, dict] = {}
    for selector, decls in _RULE_RE.findall(css_text):
        for name, needles in _COMPONENT_ARCHETYPES:
            if name in found:
                continue
            if _selector_matches(selector, needles):
                recipe = _recipe_from_decls(decls)
                if recipe:
                    found[name] = {"name": name, "anatomy": [], "recipe": recipe}
    return [found[name] for name, _ in _COMPONENT_ARCHETYPES if name in found]


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


def _build_logo_candidates(
    parser: _BrandParser, base_url: str, inline_svgs: list[str]
) -> list[dict]:
    cands: list[dict] = []

    def add(
        role: str, src: str, *, context: str = "", theme: str = "any", extra: dict | None = None
    ) -> None:
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
        add(
            role,
            icon["href"],
            context=f"rel={rel} sizes={icon['sizes']}",
            extra={"declared_color": icon.get("color", "")},
        )

    for key, role in (("og:image", "og-image"), ("twitter:image", "twitter-image")):
        if key in parser.metas:
            add(role, parser.metas[key], context=f"meta {key}")

    for img in parser.img_logos:
        role = (
            "header-logo"
            if img["region"] in ("header", "nav")
            else ("footer-logo" if img["region"] == "footer" else "body-logo")
        )
        add(
            role,
            img["src"],
            context=f"<img> in <{img['region']}> alt={img['alt']!r}",
            extra={"width": img["width"], "height": img["height"]},
        )

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


def _rank_palette(
    color_counts: Counter, theme_color: str | None, custom_props: dict[str, str]
) -> list[dict]:
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
            palette.append(
                {
                    "value": tc,
                    "role": "primary",
                    "source": "theme-color-meta",
                    "name": "theme-color",
                }
            )
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


def _rank_fonts(
    font_counts: Counter, font_links: list[str], css_text: str
) -> tuple[list[dict], list[str]]:
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
        fonts.append(
            {"family": fam, "source": "font-family", "count": font_counts[fam], "role": role}
        )
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


# --------------------------------------------------------------------------- #
# Emit-time value sanitization  [RT1-#5]
# --------------------------------------------------------------------------- #
#
# ported from design-clone/sanitizers.py — keep in sync.
#
# `_write_brand_css` writes CSS custom properties into brand.css, which the generated
# report `<link>`s. A reference-derived value passed through VERBATIM is an injection
# vector: `--x: #fff url(https://attacker/beacon.png)` becomes an exfil beacon the
# moment the report is opened. So EVERY emitted value is routed through an allowlist:
# it is kept ONLY if it is, in full, a matched color / length / number / shadow;
# anything carrying url()/var()/a non-color function/;{}@/injection metachar drops the
# WHOLE declaration (no partial salvage). No cross-skill Python import exists in this
# repo, so these are the minimal primitives ported from the design-clone skill (the
# `_scrub.sh` duplicate-until-a-third-caller precedent). Proven by Gate 193.
_SAN_HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
_SAN_FUNC_COLOR_RE = re.compile(r"^(?:rgb|rgba|hsl|hsla)\([0-9.,%\s/]+\)$")
_SAN_KEYWORD_RE = re.compile(r"^[a-zA-Z][a-zA-Z-]{0,31}$")
# LINEAR — disjoint alternation branches (digit vs `.`), no nested quantifier (ReDoS).
_SAN_LENGTH_RE = re.compile(r"^-?(?:\d+\.?\d*|\.\d+)(?:px|rem|em|%|vw|vh|ch|ex)$")
_SAN_NUMBER_RE = re.compile(r"^\d+(?:\.\d+)?$")
_SAN_FORBIDDEN = (";", "{", "}", "/*", "*/", "\\", "<", ">", "@import", "expression(", "var(")
_SAN_MAX_LAYERS = 8
_SAN_MAX_LENGTHS_PER_LAYER = 4


def _san_has_forbidden(v: str) -> bool:
    low = v.lower()
    if any(tok in low for tok in _SAN_FORBIDDEN):
        return True
    return any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in v)


def _san_color(value: str) -> str | None:
    v = str(value).strip()
    if _SAN_HEX_RE.match(v) or _SAN_FUNC_COLOR_RE.match(v) or _SAN_KEYWORD_RE.match(v):
        return v
    return None


def _san_length(value: str) -> str | None:
    v = str(value).strip()
    if not v or _san_has_forbidden(v) or "(" in v or ")" in v:
        return None
    if v == "0":
        return "0"
    return v if _SAN_LENGTH_RE.match(v) else None


def _san_number(value: str) -> str | None:
    v = str(value).strip()
    if not v or _san_has_forbidden(v) or "(" in v or ")" in v:
        return None
    return v if _SAN_NUMBER_RE.match(v) else None


def _san_split_top_level(s: str, sep_chars: str) -> list[str] | None:
    """Split on any `sep_chars` at paren-depth 0 (so a comma/space inside rgba(…) is
    preserved). None on unbalanced parens. Single linear pass, no backtracking."""
    out: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in s:
        if ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return None
            buf.append(ch)
        elif depth == 0 and ch in sep_chars:
            out.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if depth != 0:
        return None
    out.append("".join(buf))
    return out


def _san_shadow_layer_ok(layer: str) -> bool:
    toks = _san_split_top_level(layer, " ")
    if toks is None:
        return False
    toks = [t.strip() for t in toks if t.strip()]
    if not toks:
        return False
    lengths = 0
    for tok in toks:
        if tok == "inset":
            continue
        if _san_length(tok) is not None:
            lengths += 1
            if lengths > _SAN_MAX_LENGTHS_PER_LAYER:
                return False
            continue
        if _san_color(tok) is not None:
            continue
        return False
    return True


def _san_shadow(value: str) -> str | None:
    v = str(value).strip()
    if not v or _san_has_forbidden(v):
        return None
    layers = _san_split_top_level(v, ",")
    if layers is None:
        return None
    layers = [layer.strip() for layer in layers]
    if not layers or len(layers) > _SAN_MAX_LAYERS:
        return None
    for layer in layers:
        if not layer or not _san_shadow_layer_ok(layer):
            return None
    return v


def _sanitize_emit_value(value: str) -> str | None:
    """Return a safe value to emit into brand.css, or None to DROP the whole
    declaration. Kept ONLY if it is, in full, a matched color / length / number /
    shadow — no partial salvage of a value carrying url()/var()/a non-color function."""
    for fn in (_san_color, _san_length, _san_number, _san_shadow):
        out = fn(value)
        if out is not None:
            return out
    return None


# Font-family names are read from the FETCHED site's CSS (untrusted). They are
# interpolated into a double-quoted `--brand-font-*` declaration, so a name
# carrying `"`, `;`, `{`, `}`, or a newline could break out of the declaration
# and inject arbitrary CSS. _FONT_FAMILY_RE already strips `;{}` but NOT the
# double-quote or line breaks — close that here before the value reaches the CSS.
def _css_font_safe(name: str) -> str:
    """Strip characters that would let a fetched font-family name break out of a
    double-quoted CSS custom-property declaration."""
    if not name:
        return "system-ui"
    cleaned = re.sub(r'[";{}\r\n]', "", str(name)).strip()
    return cleaned or "system-ui"


def _write_brand_css(brand: dict, path: str) -> None:
    palette = brand["colors"]["palette"]
    primary = _primary_color(palette)
    bg = _role_color(palette, "background", "#ffffff")
    text = _role_color(palette, "text", "#1a1a1a")
    accent = _role_color(palette, "accent", primary)
    fonts = brand["typography"]["font_families"]
    heading_font = _css_font_safe(
        next(
            (f["family"] for f in fonts if f["role"] == "heading"),
            fonts[0]["family"] if fonts else "system-ui",
        )
    )
    body_font = _css_font_safe(
        next((f["family"] for f in fonts if f["role"] == "body"), heading_font)
    )
    # [RT1-#5] Every value below is reference-derived and untrusted; route each through
    # the allowlist sanitizers before it reaches the <link>-ed stylesheet. The synthetic
    # color tokens are already normalized colors, but sanitize defensively; radius may be
    # any declared border-radius value, so allow a length OR a keyword.
    primary = _san_color(primary) or "#2563eb"
    accent = _san_color(accent) or primary
    bg = _san_color(bg) or "#ffffff"
    text = _san_color(text) or "#1a1a1a"
    radius_raw = brand["radii"][0] if brand["radii"] else "8px"
    radius = _san_length(radius_raw) or _san_color(radius_raw) or "8px"

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
        # [RT1-#5] No verbatim reference-derived value into a stylesheet, ever — a value
        # that isn't wholly a matched color/length/number/shadow is DROPPED (no salvage).
        safe = _sanitize_emit_value(value)
        if safe is None:
            continue
        lines.append(f"  {name}: {safe};")
    lines.append("}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def _write_report_template(brand: dict, path: str, logo_rel: str | None) -> None:
    # title / source URL come from the FETCHED site's <title>/og:site_name and are
    # written verbatim into HTML attributes and text — HTMLParser decodes entities,
    # so an entity-encoded `</title><script>…` would break out and execute when the
    # generated report is opened. Escape every externally-sourced string (the report
    # is the skill's stated deliverable, explicitly meant to be opened in a browser).
    title = html.escape(
        brand["source"].get("site_name") or brand["source"].get("title") or "Report",
        quote=True,
    )
    source_url = html.escape(str(brand["source"].get("url") or ""), quote=True)
    logo_html = (
        f'<img src="{logo_rel}" alt="{title} logo" class="brand-logo" />'
        if logo_rel
        else f'<span class="brand-wordmark">{title}</span>'
    )
    doc = f"""<!doctype html>
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
        and logo above are pulled from <code>{source_url}</code>.</p>
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
        fh.write(doc)


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
            local = lg.get("local_path") or (
                "logos/" + lg["role"] + ".svg" if lg.get("svg_markup") else "—"
            )
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
        '3. `report-template.html` is a working starter — `<link rel="stylesheet" href="brand.css">`'
        " and drop your report content into `<main>`.",
        "4. Logos are in `logos/` — pick the variant (light/dark, raster/svg) your report needs.",
        "",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #


def _identity_flags_from_brand(brand: dict) -> list[dict]:
    """Advisory identity flags the extractor can see: every logo variant and every
    non-neutral (saturated) brand color. This is the ADVISORY layer only — the apply
    path's hard no-read invariant (P3) is the real defense. Never auto-approves; every
    flag's action is "human-decision"."""
    flags: list[dict] = []
    for lg in brand.get("logos", []):
        src = lg.get("src") or lg.get("local_path") or "(inline svg)"
        flags.append(
            {
                "kind": "logo",
                "evidence": f"{lg.get('role', 'logo')} — {src}",
                "action": "human-decision",
            }
        )
    for c in brand.get("colors", {}).get("palette", []):
        val = c.get("value")
        if val and not _is_neutral(val):
            flags.append(
                {
                    "kind": "saturated-color",
                    "evidence": (
                        f"palette color {val} (role guess: {c.get('role', 'unknown')}, "
                        f"source: {c.get('source', '?')})"
                    ),
                    "action": "human-decision",
                }
            )
    return flags


def extract(
    url: str,
    out_dir: str,
    *,
    max_stylesheets: int,
    download: bool,
    timeout: int,
    entry_html: str | None = None,
) -> dict:
    notes: list[str] = []
    if not urlparse(url).scheme:
        url = "https://" + url

    if entry_html is not None:
        # Offline / test entry: the page HTML is read from a local file, so no network
        # fetch of the entry page. SUB-RESOURCE fetches (stylesheets, logos) still go
        # through the hardened _fetch — the entry override is not a hole in that guard.
        html_text = entry_html
    else:
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
            notes.append(
                f"Stopped after {max_stylesheets} stylesheets (--max-stylesheets to raise)."
            )
            break
        sheet_url = urljoin(url, href)
        body, _, sheet_err = _fetch(sheet_url, timeout, max_bytes=_MAX_CSS_BYTES)
        if body is None:
            notes.append(f"Stylesheet fetch failed ({sheet_url}): {sheet_err}")
            continue
        css_chunks.append(body.decode("utf-8", errors="replace"))
        fetched_sheets += 1
    css_text = "\n".join(css_chunks)

    # --- Design schema (declared CSS only; every dimension capture_method:"static") ---
    base_unit, spacing_scale, spacing_note = _derive_spacing_scale(_collect_spacing(css_text))
    type_base, type_ratio, type_sizes, type_note = _derive_type_scale(_collect_font_sizes(css_text))
    shadows = _rank_elevation(_collect_shadows(css_text))
    grid = _derive_grid(css_text, _collect_breakpoints(css_text))
    components = _collect_component_hints(css_text)
    schema_notes = [n for n in (spacing_note, type_note) if n]

    color_counts = _collect_colors(css_text)
    custom_props = _collect_custom_properties(css_text)
    # Keep only custom properties whose value contains a color (the brand-relevant ones).
    color_props = {
        n: v
        for n, v in custom_props.items()
        if any(rx.search(v) for rx in (_HEX_RE, _RGB_RE, _HSL_RE))
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
        notes.append(
            "No brand colors detected — the site may load CSS via JS or from blocked origins."
        )
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
        (
            lg.get("local_path")
            for lg in logos
            if lg["role"] in ("header-logo", "inline-svg") and lg.get("local_path")
        ),
        next((lg.get("local_path") for lg in logos if lg.get("local_path")), None),
    )
    _write_report_template(brand, os.path.join(out_dir, "report-template.html"), primary_logo)
    _write_summary(brand, os.path.join(out_dir, "brand-summary.md"))

    # design-schema.json — the DESIGN schema (spacing/type/grid/elevation/components),
    # a NEW output that leaves brand.json / brand.css / report / summary untouched. Every
    # dimension is capture_method:"static" (declared CSS only; no browser CSSOM), and the
    # per-dimension null-degrade is carried in confidence_notes. Validated by
    # plugins/ravenclaude-core/scripts/check-design-schema.py.
    ds_source: dict = {"url": url, "fetched_at": brand["source"]["fetched_at"]}
    if parser.title:
        ds_source["title"] = parser.title
    design_schema = {
        "$schema": "https://github.com/mcorbett51090/RavenClaude/schemas/design-schema.schema.json",
        "source": ds_source,
        "capture_method": "static",
        "spacing": {
            "base_unit": base_unit,
            "scale": spacing_scale,
            "capture_method": "static",
        },
        "type_scale": {
            "base_size": type_base,
            "ratio": type_ratio,
            "sizes": type_sizes,
            "capture_method": "static",
        },
        "grid": grid,
        "elevation": {"shadows": shadows, "capture_method": "static"},
        "components": components,
        "brand_kit_ref": "brand.json",
        "identity_flags": _identity_flags_from_brand(brand),
        "confidence_notes": schema_notes,
    }
    with open(os.path.join(out_dir, "design-schema.json"), "w", encoding="utf-8") as fh:
        json.dump(design_schema, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return brand


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Extract logos + brand design tokens from a website home page."
    )
    ap.add_argument("url", help="Home page URL (scheme optional; https assumed).")
    ap.add_argument("--out", default="brand-kit", help="Output directory (default: brand-kit/).")
    ap.add_argument(
        "--max-stylesheets",
        type=int,
        default=8,
        help="Max external stylesheets to fetch (default: 8).",
    )
    ap.add_argument(
        "--no-download", action="store_true", help="Inventory logos without downloading the bytes."
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=_DEFAULT_TIMEOUT,
        help=f"Per-request timeout (default: {_DEFAULT_TIMEOUT}s).",
    )
    ap.add_argument(
        "--html-file",
        help="Read the entry-page HTML from a local file instead of fetching <url> "
        "(sub-resources are still fetched, hardened). For offline analysis / tests.",
    )
    args = ap.parse_args(argv)

    entry_html = None
    if args.html_file:
        entry_html = Path(args.html_file).read_text(encoding="utf-8", errors="replace")

    brand = extract(
        args.url,
        args.out,
        max_stylesheets=args.max_stylesheets,
        download=not args.no_download,
        timeout=args.timeout,
        entry_html=entry_html,
    )
    n_logos = len(brand["logos"])
    n_colors = len(brand["colors"]["palette"])
    n_fonts = len(brand["typography"]["font_families"])
    print(f"Brand kit written to {args.out}/")
    print(f"  logos: {n_logos}   colors: {n_colors}   fonts: {n_fonts}")
    print(
        "  files: brand.json, brand.css, design-schema.json, report-template.html, "
        "brand-summary.md, logos/"
    )
    if brand["confidence_notes"]:
        print("  notes:")
        for note in brand["confidence_notes"]:
            print(f"    - {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
