#!/usr/bin/env python3
"""render_ascii.py — deterministic ASCII/box-drawing wireframe renderer (/wireframe v1.1).

Consumes the packed layout from `_layout.pack(model)` and draws a pure-ASCII box frame — one
character per grid unit (`1 unit = 1 char`). Byte-deterministic: fixed document-order box walk,
pure ASCII glyphs (`+ - |`), LF newlines, no locale/timestamps (cross-platform-determinism).

Border-forgery safety (RT-4): every label is routed through `wireframe_lint.ascii_text` (strips
C0 controls + collapses newlines) and then CLIPPED to its cell interior width — a `-`/`|`/`+`
inside a label can never extend the frame drawn at fixed columns, so the sanitizer never has to
strip those glyphs (which would invert a KPI ``-12%`` into ``12%``).

Stdlib-only; `from __future__ import annotations` for stock-macOS Python 3.9 (RT-5).

CLI:
  --self-test      run the bundled contract checks (determinism + ASCII-only + RT-4 + structure).
  --emit FILE      render a model JSON file to ASCII on stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _layout  # noqa: E402  (sibling module, resolved via the path insert above)
from wireframe_lint import ascii_text  # noqa: E402


def _put(grid: list[list[str]], r: int, c: int, ch: str) -> None:
    if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
        grid[r][c] = ch


def _label_for(box: dict) -> str:
    if box["kind"] == "region":
        return ascii_text(box["role"]).upper()
    if box["kind"] == "component":
        role = ascii_text(box["role"])
        label = ascii_text(box["label"])
        return f"{role}: {label}" if label and label != role else role
    return ascii_text(box["label"])


def _draw_box(grid: list[list[str]], box: dict) -> None:
    x, y, w, h = box["x"], box["y"], box["w"], box["h"]
    x2, y2 = x + w - 1, y + h - 1
    for c in range(x + 1, x2):
        _put(grid, y, c, "-")
        _put(grid, y2, c, "-")
    for r in range(y + 1, y2):
        _put(grid, r, x, "|")
        _put(grid, r, x2, "|")
    for cr, cc in ((y, x), (y, x2), (y2, x), (y2, x2)):
        _put(grid, cr, cc, "+")
    # Label on the first interior row, clipped to the interior width (RT-4).
    interior_w = w - 2
    if h > 2 and interior_w > 0:
        text = _label_for(box)[:interior_w]
        for i, ch in enumerate(text):
            _put(grid, y + 1, x + 1 + i, ch)


def _render_screen(screen: dict) -> str:
    w, h = screen["w"], screen["h"]
    grid = [[" " for _ in range(w)] for _ in range(h)]
    for box in screen["boxes"]:  # parent-before-child order → children overwrite cleanly
        _draw_box(grid, box)
    return "\n".join("".join(row).rstrip() for row in grid)


def render(model: dict) -> str:
    layout = _layout.pack(model)
    screens = layout["screens"]
    parts: list[str] = []
    multi = len(screens) > 1
    for scr in screens:
        if multi:
            parts.append(f"screen: {scr['id']}")
        parts.append(_render_screen(scr))
    return "\n\n".join(parts) + "\n"


# ── bundled self-test ─────────────────────────────────────────────────────────
def _self_test() -> int:
    failures: list[str] = []

    out = render(_layout._MODEL)
    if render(_layout._MODEL) != out:
        failures.append("render() is non-deterministic")
    if any(ord(ch) > 127 for ch in out):
        failures.append("render() emitted a non-ASCII character")

    # RT-4: a '-' in a label survives (a wide kpi-stat cell shows "-12%" intact).
    kpi_model = {
        "meta": {"title": "Metrics", "type": "dashboard", "viewport": "desktop"},
        "regions": [
            {
                "role": "main",
                "sections": [
                    {
                        "kind": "kpi",
                        "components": [{"type": "kpi-stat", "props": {"label": "-12%"}}],
                    }
                ],
            }
        ],
    }
    if "-12%" not in render(kpi_model):
        failures.append("RT-4 regression: '-12%' label did not survive rendering")

    # A newline in a label must not add rows: the rendered screen height equals the packed height.
    nl_model = {
        "meta": {"title": "NL", "type": "page", "viewport": "mobile"},
        "regions": [
            {
                "role": "hero",
                "sections": [
                    {
                        "kind": "s",
                        "components": [{"type": "button", "props": {"label": "line1\nline2"}}],
                    }
                ],
            }
        ],
    }
    packed_h = _layout.pack(nl_model)["screens"][0]["h"]
    rendered_rows = _render_screen(_layout.pack(nl_model)["screens"][0]).split("\n")
    if len(rendered_rows) != packed_h:
        failures.append(
            f"row count {len(rendered_rows)} != packed height {packed_h} (newline leaked a row)"
        )

    if failures:
        print("render_ascii --self-test: FAIL")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("render_ascii --self-test: OK (determinism + ASCII-only + RT-4 + structure)")
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────────
def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Deterministic ASCII wireframe renderer.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--emit", metavar="FILE", help="render a model JSON file to ASCII")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    with open(args.emit, encoding="utf-8") as fh:
        model = json.load(fh)
    sys.stdout.write(render(model))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
