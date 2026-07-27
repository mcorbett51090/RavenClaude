#!/usr/bin/env python3
"""render_svg.py — deterministic SVG wireframe renderer (/wireframe v1.1).

Consumes the packed layout from `_layout.pack(model)` and emits a self-contained SVG using a
CLOSED vocabulary — `<svg viewBox>` / `<g>` / `<rect>` / `<text>` only. It is built to clear
`svg-report-lint` (Gate 103) BY CONSTRUCTION:
  * no `<script>`, no `on*` handlers, no `<foreignObject>`, no remote/`javascript:` href, no `<use>`;
  * every `<text>` carries `font-size="10"` (>= the 8px legibility floor);
  * the viewBox aspect is padded into [0.05, 20] universally (see `_pad_aspect`) so a short or a
    multi-screen model can never render as a sliver/pillar that trips the aspect check (T1 + RT).

Determinism: integer coords, explicit PINNED attribute-emission order (never dict-insertion
reliant — CE-5), LF newlines, document-order walk. Colors/text routed through the v1 sanitizers
(`css_value` / `html_text`) — the model carries description-derived text into a shareable artifact.

Stdlib-only; `from __future__ import annotations` for stock-macOS Python 3.9 (RT-5).

CLI:
  --self-test      run the bundled contract checks (determinism + Gate-103 structure + aspect).
  --emit FILE      render a model JSON file to SVG on stdout.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _layout  # noqa: E402
from wireframe_lint import css_value, html_text  # noqa: E402

PX = _layout.GRID_UNIT_PX  # grid unit -> pixels
GAP = 4  # inter-screen gap (units), multi-screen grid
LABEL_H = 3  # screen-title strip height (units), multi-screen grid
FONT = 10  # >= svg-report-lint's 8px floor

# Kind -> (fill, stroke). All are literal safe colors; routed through css_value anyway so the
# sanitizer path is exercised (and a future themed variant stays safe).
_STYLE = {
    "region": ("#eef2f7", "#334155"),
    "section": ("#f8fafc", "#64748b"),
    "component": ("#ffffff", "#94a3b8"),
    "slot": ("#f1f5f9", "#cbd5e1"),
}
_TEXT_FILL = "#0f172a"


def _color(value: str, fallback: str) -> str:
    """css_value returns the value iff it is a safe color, else None -> fallback."""
    return css_value(value) or fallback


def _rect(x: int, y: int, w: int, h: int, fill: str, stroke: str) -> str:
    # PINNED attribute order (determinism): x, y, width, height, fill, stroke, stroke-width.
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
        f'fill="{_color(fill, "#ffffff")}" stroke="{_color(stroke, "#94a3b8")}" '
        f'stroke-width="1" />'
    )


def _text(x: int, y: int, label: str, fill: str = _TEXT_FILL) -> str:
    # PINNED attribute order: x, y, font-family, font-size, fill.
    return (
        f'<text x="{x}" y="{y}" font-family="monospace" font-size="{FONT}" '
        f'fill="{_color(fill, "#0f172a")}">{html_text(label)}</text>'
    )


def _label_for(box: dict) -> str:
    if box["kind"] == "region":
        return str(box["role"]).upper()
    if box["kind"] == "component":
        role, label = str(box["role"]), str(box["label"])
        return f"{role}: {label}" if label and label != role else role
    return str(box["label"])


def _screen_body(screen: dict, ox: int, oy: int) -> list[str]:
    """Emit one screen's rects+texts, offset by (ox, oy) in GRID UNITS."""
    out: list[str] = []
    for box in screen["boxes"]:  # parent-before-child order
        fill, stroke = _STYLE.get(box["kind"], _STYLE["component"])
        px = (box["x"] + ox) * PX
        py = (box["y"] + oy) * PX
        out.append(_rect(px, py, box["w"] * PX, box["h"] * PX, fill, stroke))
        if box["h"] > 2 and box["w"] > 3:
            # Truncate to roughly fit the box width (~6px/char at 10px monospace).
            max_chars = max(1, (box["w"] * PX - 8) // 6)
            label = _label_for(box)[:max_chars]
            out.append(_text(px + 4, py + FONT + 3, label))
    return out


def _pad_aspect(cw: int, ch: int) -> tuple[int, int]:
    """Pad a content bbox (units) so its aspect lands in svg-report-lint's [0.05, 20] window.

    Padding only ever GROWS a dimension (adds whitespace), so content never clips. Guarantees a
    valid viewBox for any single- or multi-screen model regardless of the packer's own clamp.
    """
    cw = max(1, cw)
    ch = max(1, ch)
    vb_w = max(cw, _layout._ceil_div(ch, 20))  # aspect >= 0.05
    vb_h = max(ch, _layout._ceil_div(cw, 20))  # aspect <= 20
    return vb_w, vb_h


def render(model: dict) -> str:
    layout = _layout.pack(model)
    screens = layout["screens"]
    body: list[str] = []

    if len(screens) == 1:
        scr = screens[0]
        body += _screen_body(scr, 0, 0)
        cw, ch = scr["w"], scr["h"]
    else:
        n = len(screens)
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        cell_w = max(s["w"] for s in screens)
        cell_h = max(s["h"] for s in screens)
        for i, scr in enumerate(screens):
            r, c = divmod(i, cols)
            ox = c * (cell_w + GAP)
            oy = r * (cell_h + LABEL_H + GAP)
            body.append(_text(ox * PX + 2, oy * PX + FONT, f"screen: {scr['id']}"))
            body += _screen_body(scr, ox, oy + LABEL_H)
        cw = cols * (cell_w + GAP) - GAP
        ch = rows * (cell_h + LABEL_H + GAP) - GAP

    vb_w, vb_h = _pad_aspect(cw * PX, ch * PX)
    header = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb_w} {vb_h}" '
        f'width="{vb_w}" height="{vb_h}">'
    )
    lines = [header, '<rect x="0" y="0" width="%d" height="%d" fill="#ffffff" />' % (vb_w, vb_h)]
    lines += body
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


# ── bundled self-test ─────────────────────────────────────────────────────────
_FORBIDDEN = ("<script", "foreignobject", "javascript:", "http://", "https://")


def _structural_ok(svg: str, failures: list[str]) -> None:
    low = svg.lower()
    for bad in _FORBIDDEN:
        # allow the xmlns namespace URL (it is not a fetchable href/use)
        if bad in ("http://", "https://"):
            stripped = low.replace('xmlns="http://www.w3.org/2000/svg"', "")
            if bad in stripped:
                failures.append(f"SVG contains a remote URL ({bad})")
            continue
        if bad in low:
            failures.append(f"SVG contains forbidden token {bad!r}")
    import re as _re

    if _re.search(r"\son\w+\s*=", svg):
        failures.append("SVG contains an on* event handler")
    if 'viewBox="' not in svg:
        failures.append("SVG missing viewBox")
    if 'font-size="10"' not in svg:
        failures.append("SVG text below the 8px legibility floor")


def _aspect(svg: str) -> float:
    import re as _re

    m = _re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    w, h = int(m.group(1)), int(m.group(2))
    return w / h


def _self_test() -> int:
    failures: list[str] = []

    out = render(_layout._MODEL)
    if render(_layout._MODEL) != out:
        failures.append("render() is non-deterministic")
    _structural_ok(out, failures)
    a = _aspect(out)
    if not (0.05 <= a <= 20):
        failures.append(f"single-screen viewBox aspect {a:.3f} outside 0.05..20")

    # Aspect padding must hold for a short model AND a multi-screen model.
    short = {
        "meta": {"title": "S", "type": "page", "viewport": "desktop"},
        "regions": [{"role": "footer", "sections": [{"kind": "k"}]}],
    }
    if not (0.05 <= _aspect(render(short)) <= 20):
        failures.append("short-model viewBox aspect outside range")
    multi = {
        "meta": {"title": "App", "type": "app-screen", "model_version": "2"},
        "screens": [
            {"id": f"s{i}", "regions": [{"role": "main", "sections": [{"kind": "k"}]}]}
            for i in range(5)
        ],
    }
    ms = render(multi)
    _structural_ok(ms, failures)
    if not (0.05 <= _aspect(ms) <= 20):
        failures.append(f"multi-screen viewBox aspect {_aspect(ms):.3f} outside 0.05..20")

    if failures:
        print("render_svg --self-test: FAIL")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("render_svg --self-test: OK (determinism + Gate-103 structure + aspect padding)")
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────────
def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Deterministic SVG wireframe renderer.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--emit", metavar="FILE", help="render a model JSON file to SVG")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    with open(args.emit, encoding="utf-8") as fh:
        model = json.load(fh)
    sys.stdout.write(render(model))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
