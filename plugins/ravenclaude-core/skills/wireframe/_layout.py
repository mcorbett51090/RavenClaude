#!/usr/bin/env python3
"""_layout.py — the shared deterministic coordinate/box-packer behind /wireframe v1.1.

Turns a validated wireframe MODEL (schemas/wireframe-model.schema.json) into absolute
integer-grid-unit boxes that the ASCII (`render_ascii.py`) and SVG (`render_svg.py`)
renderers consume. One packer, two renderers.

Design invariants (FORGE v1.1 tiebreaks + red-team):
  * Integer grid units only — no float coords (byte-determinism; cross-platform-determinism).
  * Container-relative sizing — a component takes its CONTAINER's width, never a fixed
    footprint, so a `table` on a narrow mobile canvas can never exceed the canvas (RT-2).
  * The packer is TOTAL: it never crashes on any model the validator accepts. `columns:0`
    parses to 1 column (RT-2); every emitted dimension is floored at 1 (RT-3); a child is
    clamped to its container; content taller than the canvas cap is truncated, never scaled
    (avoids RT-3 integer-compression rounding).
  * Canvas height is clamped into [ceil(W/20), 20*W] so the SVG viewBox aspect W/H always
    lands in svg-report-lint's 0.05..20 window at BOTH ends (T1 union clamp; Gate 103).
  * Non-overlap is structural (rectangle subdivision → disjoint siblings). The two-predicate
    self-check (sibling AABB-disjoint + child-within-parent, mirroring pbir-layout-engine's
    check_no_overlap / check_within_canvas) is a REGRESSION PROOF, and `--self-test` proves it
    has teeth with a hand-built overlapping box-set (a packer never emits overlap, so the teeth
    cannot come from a model — RT-8).

Stdlib-only. `from __future__ import annotations` so PEP-604 unions don't crash on stock-macOS
Python 3.9 (RT-5; the same macOS-door class the repo already fixes elsewhere).

CLI:
  --self-test        run the bundled contract checks (pack determinism + self-check teeth).
  --pack FILE        print the packed layout as JSON (debug only; NOT a committed golden —
                     json.dumps vs prettier array-inlining is unsatisfiable, RT-1).
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# ── grid + viewport ───────────────────────────────────────────────────────────
GRID_UNIT_PX = 8
VIEWPORT_WIDTH = {"desktop": 120, "responsive": 120, "tablet": 90, "mobile": 40}
DEFAULT_WIDTH = 120

# ── nominal heights (grid units); every leaf floors at MIN_LEAF_H ─────────────
MIN_LEAF_H = 3
DEFAULT_COMPONENT_H = 3
COMPONENT_H = {
    "button": 3,
    "input": 3,
    "form": 8,
    "card": 6,
    "table": 8,
    "chart": 8,
    "kpi-stat": 4,
    "list": 6,
    "tabs": 3,
    "breadcrumb": 3,
    "search": 3,
    "avatar": 4,
    "badge": 3,
    "toggle": 3,
    "stepper": 3,
    "nav-item": 3,
    "node": 4,
    "edge": 3,
}
SLOT_H = {"text": 3, "image-box": 6, "data-shape": 5}
HEADING_H = 2
MIN_SECTION_H = 4
MIN_REGION_H = 4
MAX_LABEL = 60


# ── small deterministic helpers ───────────────────────────────────────────────
def _ceil_div(a: int, b: int) -> int:
    return -(-a // b)


def _clean_label(s: object) -> str:
    """A sane box label: strip C0 controls + newlines/tabs, collapse, truncate.

    This is the box-level label hygiene. The ASCII renderer additionally CLIPS to the
    cell interior at render time (so a `-`/`|` in a label can never forge a border — RT-4),
    which is why this does NOT strip structural glyphs.
    """
    text = "" if s is None else str(s)
    text = re.sub(r"[\x00-\x1f\x7f]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:MAX_LABEL]


def _viewport_width(model: dict) -> int:
    vp = (model.get("meta") or {}).get("viewport", "responsive")
    return VIEWPORT_WIDTH.get(vp, DEFAULT_WIDTH)


def _region_cols(region: dict) -> int:
    """Columns a region's sections split into — defensive (RT-2: never 0/negative)."""
    layout = region.get("layout", "stack")
    detail = str(region.get("layout_detail", "") or "")
    nums = [int(n) for n in re.findall(r"\d+", detail)]
    if layout == "stack":
        return 1
    if layout == "split":
        return 2
    if layout == "grid":
        cols = nums[1] if len(nums) >= 2 else (nums[0] if nums else 2)
    else:  # row / columns
        cols = nums[0] if nums else 2
    return cols if cols > 0 else 1


def _item_h(item: object) -> int:
    if isinstance(item, dict) and "slot" in item:
        base = SLOT_H.get(item.get("slot"), MIN_LEAF_H)
    else:
        base = COMPONENT_H.get(
            (item or {}).get("type") if isinstance(item, dict) else None, DEFAULT_COMPONENT_H
        )
    return max(MIN_LEAF_H, base)


def _item_meta(item: dict) -> tuple[str, str, str]:
    """(kind, role, label) for a slot or component."""
    if "slot" in item:
        props_text = item.get("text")
        return "slot", str(item.get("slot", "slot")), _clean_label(props_text or item.get("slot"))
    props = item.get("props") or {}
    role = str(item.get("type", "component"))
    return "component", role, _clean_label(props.get("label") or role)


# ── model → screens (v1 regions XOR v2 screens) ───────────────────────────────
def normalize_to_screens(model: dict) -> list[dict]:
    """The single renderer entry: every model becomes a list of {id, regions[]} screens.

    v1 (`regions`) → one screen; v2 (`screens`) → N screens. Both renderers consume only
    this shape, so no renderer is ever stranded on a model version (RT-6).
    """
    if isinstance(model.get("screens"), list) and model["screens"]:
        out = []
        for i, scr in enumerate(model["screens"]):
            sid = str((scr or {}).get("id") or f"screen-{i + 1}")
            out.append({"id": sid, "regions": (scr or {}).get("regions", []) or []})
        return out
    title = (model.get("meta") or {}).get("title") or "screen-1"
    return [{"id": _slug(title), "regions": model.get("regions", []) or []}]


def _slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9-]+", "-", str(text).lower()).strip("-")
    return s or "screen"


# ── measurement (bottom-up) ───────────────────────────────────────────────────
def _measure_section(section: dict) -> int:
    h = 3  # top border + one label row (heading/kind) + bottom border
    items = list(section.get("content_slots") or []) + list(section.get("components") or [])
    for it in items:
        h += _item_h(it)
    return max(MIN_SECTION_H, h)


def _measure_region(region: dict, width: int) -> int:
    sections = region.get("sections") or []
    cols = min(_region_cols(region), max(1, width - 2))
    col_h = [0] * cols
    for i, sec in enumerate(sections):
        col_h[i % cols] += _measure_section(sec)
    inner = max(col_h) if col_h else MIN_SECTION_H
    return max(MIN_REGION_H, inner + 3)  # top border + region label row + bottom border


# ── packing (top-down coordinate assignment) ──────────────────────────────────
def _box(
    state: dict,
    parent: int,
    x: int,
    y: int,
    w: int,
    h: int,
    kind: str,
    role: str,
    label: str,
    emphasis: object,
) -> int:
    b = {
        "id": state["next_id"],
        "parent": parent,
        "x": int(x),
        "y": int(y),
        "w": max(1, int(w)),
        "h": max(1, int(h)),
        "kind": kind,
        "role": str(role),
        "label": label,
        "emphasis": emphasis,
    }
    state["next_id"] += 1
    state["boxes"].append(b)
    return b["id"]


def _emit_section(state: dict, section: dict, parent: int, x: int, y: int, w: int, h: int) -> None:
    sid = _box(
        state,
        parent,
        x,
        y,
        w,
        h,
        "section",
        section.get("kind", "section"),
        _clean_label(section.get("heading") or section.get("kind", "section")),
        section.get("emphasis"),
    )
    ix, iy = x + 1, y + 1
    iw, ih = max(1, w - 2), max(1, h - 2)
    cy = iy + 1  # row iy is the section label (heading/kind), drawn by the renderer
    items = list(section.get("content_slots") or []) + list(section.get("components") or [])
    for it in items:
        if not isinstance(it, dict):
            continue
        avail = (iy + ih) - cy
        if avail < 1:
            break
        hh = min(_item_h(it), avail)
        kind, role, label = _item_meta(it)
        _box(state, sid, ix, cy, iw, hh, kind, role, label, None)
        cy += hh


def _emit_region(state: dict, region: dict, x: int, y: int, w: int, h: int) -> None:
    rid = _box(
        state,
        -1,
        x,
        y,
        w,
        h,
        "region",
        region.get("role", "region"),
        _clean_label(region.get("role", "region")),
        region.get("emphasis"),
    )
    ix, iy = x + 1, y + 1
    iw, ih = max(1, w - 2), max(1, h - 2)
    sections = region.get("sections") or []
    cols = min(_region_cols(region), max(1, iw))
    col_w = max(1, iw // cols)
    col_x = [ix + c * col_w for c in range(cols)]
    widths = [col_w] * cols
    widths[-1] = max(1, (ix + iw) - col_x[-1])  # last column absorbs the remainder
    col_y = [iy + 1] * cols  # row iy is the region label, drawn by the renderer
    for i, sec in enumerate(sections):
        if not isinstance(sec, dict):
            continue
        c = i % cols
        avail = (iy + ih) - col_y[c]
        if avail < 1:
            continue
        sh = min(_measure_section(sec), avail)
        _emit_section(state, sec, rid, col_x[c], col_y[c], widths[c], sh)
        col_y[c] += sh


def _pack_screen(screen: dict, width: int) -> dict:
    max_h = 20 * width
    min_h = _ceil_div(width, 20)
    state: dict = {"boxes": [], "next_id": 0}
    y = 0
    for region in screen.get("regions", []) or []:
        if not isinstance(region, dict):
            continue
        if y >= max_h:
            break
        avail = max_h - y
        if avail < MIN_REGION_H:
            break
        rh = min(_measure_region(region, width), avail)
        _emit_region(state, region, 0, y, width, rh)
        y += rh
    canvas_h = max(min_h, min(y, max_h), 1)
    return {"id": screen["id"], "w": width, "h": canvas_h, "boxes": state["boxes"]}


def pack(model: dict) -> dict:
    """Model → {canvas_w, grid_unit_px, screens:[{id, w, h, boxes[]}]}."""
    width = _viewport_width(model)
    screens = [_pack_screen(scr, width) for scr in normalize_to_screens(model)]
    return {"canvas_w": width, "grid_unit_px": GRID_UNIT_PX, "screens": screens}


# ── self-checks (the two predicates, T4) ──────────────────────────────────────
def check_within_canvas(boxes: list[dict], w: int, h: int) -> list[str]:
    bad = []
    for b in boxes:
        if b["x"] < 0 or b["y"] < 0 or b["x"] + b["w"] > w or b["y"] + b["h"] > h:
            bad.append(f"box {b['id']} ({b['role']}) extends outside {w}x{h} canvas")
    return bad


def check_no_overlap(boxes: list[dict]) -> list[str]:
    """Siblings (same parent) must be AABB-disjoint — strict-< interval test (pbir precedent)."""
    bad = []
    groups: dict = {}
    for b in boxes:
        groups.setdefault(b["parent"], []).append(b)
    for parent in sorted(groups):
        sibs = groups[parent]
        for i in range(len(sibs)):
            for j in range(i + 1, len(sibs)):
                a, c = sibs[i], sibs[j]
                ox = a["x"] < c["x"] + c["w"] and c["x"] < a["x"] + a["w"]
                oy = a["y"] < c["y"] + c["h"] and c["y"] < a["y"] + a["h"]
                if ox and oy:
                    bad.append(f"box {a['id']} overlaps sibling {c['id']} under parent {parent}")
    return bad


def check_containment(boxes: list[dict]) -> list[str]:
    """Every non-root box must lie within its parent (containment, NOT overlap — T4)."""
    by_id = {b["id"]: b for b in boxes}
    bad = []
    for b in boxes:
        p = by_id.get(b["parent"])
        if p is None:
            continue
        if (
            b["x"] < p["x"]
            or b["y"] < p["y"]
            or b["x"] + b["w"] > p["x"] + p["w"]
            or b["y"] + b["h"] > p["y"] + p["h"]
        ):
            bad.append(f"box {b['id']} not contained in parent {b['parent']}")
    return bad


def self_check(layout: dict) -> list[str]:
    """Run all three predicates over a packed layout; empty list == clean."""
    problems = []
    for scr in layout.get("screens", []):
        problems += check_within_canvas(scr["boxes"], scr["w"], scr["h"])
        problems += check_no_overlap(scr["boxes"])
        problems += check_containment(scr["boxes"])
    return problems


# ── bundled self-test ─────────────────────────────────────────────────────────
_MODEL = {
    "meta": {"title": "Acme", "type": "page", "viewport": "desktop"},
    "regions": [
        {
            "role": "header",
            "layout": "row",
            "layout_detail": "2",
            "sections": [
                {
                    "kind": "brand",
                    "heading": "Acme",
                    "components": [{"type": "nav-item", "props": {"label": "Home"}}],
                },
                {"kind": "nav", "components": [{"type": "button", "props": {"label": "Sign in"}}]},
            ],
        },
        {
            "role": "hero",
            "emphasis": "primary",
            "sections": [
                {
                    "kind": "value-prop",
                    "heading": "Fast plumbing",
                    "content_slots": [{"slot": "text", "text": "24/7 callouts"}],
                    "components": [{"type": "button", "props": {"label": "Book"}}],
                }
            ],
        },
        {
            "role": "main",
            "layout": "columns",
            "layout_detail": "0",  # RT-2: 0 -> 1 col, no crash
            "sections": [
                {"kind": "content", "components": [{"type": "card", "props": {"label": "A"}}]}
            ],
        },
    ],
}
# RT-2 stress: a model the validator accepts but that would crash a naive packer.
_MODEL_STRESS = {
    "meta": {"title": "Stress", "type": "app-screen", "viewport": "mobile"},
    "regions": [
        {
            "role": "main",
            "layout": "grid",
            "layout_detail": "9x9",  # more cols than a 40-wide canvas
            "sections": [
                {"kind": "wide", "components": [{"type": "table", "props": {"label": "Big table"}}]}
            ],
        },
    ],
}


def _self_test() -> int:
    failures: list[str] = []

    # 1. Determinism — same model packs byte-identically twice.
    a = json.dumps(pack(_MODEL), sort_keys=True)
    b = json.dumps(pack(_MODEL), sort_keys=True)
    if a != b:
        failures.append("pack() is non-deterministic")

    # 2. A real model packs cleanly (self-check silent).
    for name, m in (("_MODEL", _MODEL), ("_MODEL_STRESS", _MODEL_STRESS)):
        problems = self_check(pack(m))
        if problems:
            failures.append(f"{name}: self-check flagged a clean packed layout: {problems[:2]}")

    # 3. TEETH (RT-8): a hand-built overlapping box-set MUST be flagged. A packer never
    #    emits overlap, so the only honest teeth is a fixture built by hand.
    overlap_boxes = [
        {"id": 0, "parent": -1, "x": 0, "y": 0, "w": 10, "h": 10, "role": "a"},
        {"id": 1, "parent": -1, "x": 5, "y": 5, "w": 10, "h": 10, "role": "b"},  # overlaps 0
    ]
    if not check_no_overlap(overlap_boxes):
        failures.append("check_no_overlap FAILED to flag a hand-built overlap (no teeth)")
    disjoint_boxes = [
        {"id": 0, "parent": -1, "x": 0, "y": 0, "w": 10, "h": 10, "role": "a"},
        {
            "id": 1,
            "parent": -1,
            "x": 0,
            "y": 10,
            "w": 10,
            "h": 10,
            "role": "b",
        },  # adjacent, no overlap
    ]
    if check_no_overlap(disjoint_boxes):
        failures.append("check_no_overlap false-positived on adjacent (touching) boxes")
    out_boxes = [{"id": 0, "parent": -1, "x": 0, "y": 0, "w": 200, "h": 5, "role": "wide"}]
    if not check_within_canvas(out_boxes, 100, 100):
        failures.append("check_within_canvas FAILED to flag an out-of-canvas box (no teeth)")

    # 4. RT-2/RT-3: the stress model floors every dimension at >=1.
    for scr in pack(_MODEL_STRESS)["screens"]:
        for bx in scr["boxes"]:
            if bx["w"] < 1 or bx["h"] < 1:
                failures.append(f"degenerate box {bx['id']} (w={bx['w']}, h={bx['h']})")

    if failures:
        print("_layout --self-test: FAIL")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print("_layout --self-test: OK (pack determinism + within-canvas/overlap/containment teeth)")
    return 0


# ── CLI ───────────────────────────────────────────────────────────────────────
def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Deterministic wireframe box-packer.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test", action="store_true")
    group.add_argument("--pack", metavar="FILE", help="print packed layout JSON (debug only)")
    args = parser.parse_args(argv)

    if args.self_test:
        return _self_test()

    with open(args.pack, encoding="utf-8") as fh:
        model = json.load(fh)
    print(json.dumps(pack(model), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
