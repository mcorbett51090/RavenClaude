#!/usr/bin/env python3
"""8-point-grid layout solver for Power BI report design (report-visualization-design skill).

Given a canvas, margin, gap, and a 3-30-300-school template, emit each region's
x/y/width/height snapped to an 8px grid. The coordinates are designed to pass the
`pbir-layout-engine` linter (within-canvas, no-overlap, equal-gap, column-alignment),
so they drop straight into a PBIR page.json `position` block.

Stdlib-only. No network. No file writes. Fail-safe: bad input -> stderr + non-zero exit.

Usage:
    grid.py --template 3-30-300 [--canvas 1664x936] [--margin 16] [--gap 16] [--format json|text]
    grid.py --template kpi-strip --kpis 4
    grid.py --template golden-overview
"""
from __future__ import annotations

import argparse
import json
import sys

GRID = 8  # the 8-point grid module — every coordinate is a multiple of this


def _snap(v: float) -> int:
    """Snap a value down to the nearest 8px grid line (never negative)."""
    return max(0, int(v) // GRID * GRID)


def _snap_round(v: float) -> int:
    """Snap to the nearest grid line (for widths/heights that should fill, not shrink to 0)."""
    return max(GRID, int(round(v / GRID)) * GRID)


def _region(name: str, role: str, x: int, y: int, w: int, h: int) -> dict:
    return {"name": name, "role": role, "x": x, "y": y, "width": w, "height": h}


def template_3_30_300(canvas_w: int, canvas_h: int, margin: int, gap: int) -> list[dict]:
    """Overview (top-left) | filter band (center) | detail (bottom-right) — the 3-30-300 layout.

    Two columns: a left column (overview stacked above filter) and a right column
    (a tall hero/trend above a detail table). Equal gaps, aligned columns.
    """
    inner_w = canvas_w - 2 * margin
    inner_h = canvas_h - 2 * margin
    # two equal columns
    col_w = _snap_round((inner_w - gap) / 2)
    left_x = margin
    right_x = margin + col_w + gap
    # left column: overview (top third) + filter (lower two thirds)
    overview_h = _snap_round(inner_h / 3 - gap / 2)
    filter_y = margin + overview_h + gap
    filter_h = _snap_round(canvas_h - margin - filter_y)
    # right column: trend (top third) + detail (lower two thirds), aligned to left rows
    detail_y = filter_y
    detail_h = filter_h
    return [
        _region("overview-kpis", "3s-overview", left_x, margin, col_w, overview_h),
        _region("trend", "3s-overview", right_x, margin, col_w, overview_h),
        _region("filter-breakdowns", "30s-filter", left_x, filter_y, col_w, filter_h),
        _region("detail-table", "300s-detail", right_x, detail_y, col_w, detail_h),
    ]


def template_kpi_strip(canvas_w: int, canvas_h: int, margin: int, gap: int, kpis: int) -> list[dict]:
    """N equal KPI cards across the top — the headline strip (Buhler: keep to 3-4)."""
    if kpis < 1:
        raise ValueError("--kpis must be >= 1")
    inner_w = canvas_w - 2 * margin
    total_gap = gap * (kpis - 1)
    card_w = _snap_round((inner_w - total_gap) / kpis)
    card_h = _snap_round((canvas_h - 2 * margin) / 6)  # a slim top strip
    out = []
    x = margin
    for i in range(kpis):
        out.append(_region(f"kpi-{i + 1}", "3s-overview", x, margin, card_w, card_h))
        x += card_w + gap
    return out


def template_golden_overview(canvas_w: int, canvas_h: int, margin: int, gap: int) -> list[dict]:
    """One hero visual (left ~2/3) + a supporting column (right ~1/3)."""
    inner_w = canvas_w - 2 * margin
    inner_h = canvas_h - 2 * margin
    hero_w = _snap_round(inner_w * 2 / 3 - gap / 2)
    side_w = _snap_round(inner_w - hero_w - gap)
    side_x = margin + hero_w + gap
    half_h = _snap_round((inner_h - gap) / 2)
    return [
        _region("hero", "3s-overview", margin, margin, hero_w, inner_h),
        _region("support-top", "30s-filter", side_x, margin, side_w, half_h),
        _region("support-bottom", "300s-detail", side_x, margin + half_h + gap, side_w, half_h),
    ]


TEMPLATES = {
    "3-30-300": template_3_30_300,
    "kpi-strip": template_kpi_strip,
    "golden-overview": template_golden_overview,
}


def _parse_canvas(s: str) -> tuple[int, int]:
    try:
        w, h = s.lower().split("x")
        return int(w), int(h)
    except Exception as exc:  # noqa: BLE001 — fail-safe wrapper
        raise ValueError(f"--canvas must be WxH (e.g. 1664x936); got {s!r}") from exc


def _validate(regions: list[dict], canvas_w: int, canvas_h: int) -> None:
    """Self-check: every region within canvas, grid-aligned, and pairwise non-overlapping."""
    for r in regions:
        if r["x"] % GRID or r["y"] % GRID or r["width"] % GRID or r["height"] % GRID:
            raise AssertionError(f"region {r['name']} is not 8px-grid aligned: {r}")
        if r["x"] < 0 or r["y"] < 0:
            raise AssertionError(f"region {r['name']} has negative origin: {r}")
        if r["x"] + r["width"] > canvas_w or r["y"] + r["height"] > canvas_h:
            raise AssertionError(f"region {r['name']} exceeds canvas {canvas_w}x{canvas_h}: {r}")
    for i in range(len(regions)):
        for j in range(i + 1, len(regions)):
            a, b = regions[i], regions[j]
            overlap = (
                a["x"] < b["x"] + b["width"]
                and b["x"] < a["x"] + a["width"]
                and a["y"] < b["y"] + b["height"]
                and b["y"] < a["y"] + a["height"]
            )
            if overlap:
                raise AssertionError(f"regions {a['name']} and {b['name']} overlap: {a} {b}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="8-pt-grid layout solver for Power BI report design.")
    p.add_argument("--template", required=True, choices=sorted(TEMPLATES))
    p.add_argument("--canvas", default="1664x936", help="WxH canvas size (default 1664x936)")
    p.add_argument("--margin", type=int, default=16, help="outer margin px (default 16)")
    p.add_argument("--gap", type=int, default=16, help="gap between visuals px (default 16)")
    p.add_argument("--kpis", type=int, default=4, help="KPI count for kpi-strip (default 4)")
    p.add_argument("--format", default="json", choices=("json", "text"))
    args = p.parse_args(argv)

    try:
        canvas_w, canvas_h = _parse_canvas(args.canvas)
        if canvas_w < 8 * GRID or canvas_h < 8 * GRID:
            raise ValueError(f"canvas too small: {args.canvas}")
        if args.margin < 0 or args.gap < 0:
            raise ValueError("--margin and --gap must be >= 0")
        fn = TEMPLATES[args.template]
        if args.template == "kpi-strip":
            regions = fn(canvas_w, canvas_h, args.margin, args.gap, args.kpis)
        else:
            regions = fn(canvas_w, canvas_h, args.margin, args.gap)
        _validate(regions, canvas_w, canvas_h)
    except Exception as exc:  # noqa: BLE001 — fail-safe: one diagnostic, non-zero exit
        print(f"grid.py: {exc}", file=sys.stderr)
        return 2

    payload = {
        "template": args.template,
        "canvas": {"width": canvas_w, "height": canvas_h},
        "grid_px": GRID,
        "margin_px": args.margin,
        "gap_px": args.gap,
        "regions": regions,
    }
    if args.format == "json":
        print(json.dumps(payload, indent=2))
    else:
        print(f"{args.template} on {canvas_w}x{canvas_h} (grid={GRID}, margin={args.margin}, gap={args.gap})")
        for r in regions:
            print(f"  {r['name']:<20} [{r['role']:<12}] x={r['x']:<5} y={r['y']:<5} w={r['width']:<5} h={r['height']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
