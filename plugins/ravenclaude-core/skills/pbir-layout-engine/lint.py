#!/usr/bin/env python3
"""Layout-arithmetic linter for dashboard/report page definitions.

This is the load-bearing, deterministic artifact behind the `data-viz-designer`
agent: it checks that a page's visuals satisfy hard layout arithmetic (no
overlap, within canvas, equal gaps, aligned columns) and — for Power BI PBIR
Enhanced inputs — three PBIR-specific invariants (no empty query bindings, a
bounded count of theme overrides, and schema validity of the `visualType` /
`displayOption` enums).

Purity / dependency contract
----------------------------
The linter is stdlib-only (no third-party imports) and has NO network access.
It reads exactly two kinds of input from the filesystem:

  1. The user-supplied `<input-path>` (a page JSON, a page directory, or a
     fixture directory).  The path MUST NOT contain "..", and MUST resolve
     inside the repository root; otherwise the process exits 2 (purity-contract
     failure).

  2. ONE sanctioned cross-plugin read:
        plugins/power-platform/knowledge/pbir-enhanced-reference.md  § 1
     This Markdown file is the canon-of-record for the PBIR `visualType` enum.
     The linter parses § 1 ("Visual type -> queryState role mapping") at runtime
     to obtain the set of valid `visualType` strings used by check-7.  This is
     the ONLY cross-plugin filesystem dependency in the linter, and it is
     deliberate: the enum lives in the power-platform plugin's knowledge bank,
     not duplicated here, so the two cannot silently drift (audit-gates Gate 51
     watches that drift; this linter is the runtime consumer).  If § 1 cannot be
     located or parsed, check-7 cannot run and the process exits 3
     (schema-enum parse failure).  When the reference file is genuinely absent
     (e.g. ravenclaude-core installed without power-platform), `--no-pbir`
     inputs are unaffected; only PBIR `visualType` validation degrades.

Exit codes (see the build plan "Linter CLI" contract)
-----------------------------------------------------
  0   All checks pass (or only info-level Findings).
  1   One or more Findings of error severity (or warning when --strict).
  2   I/O error, parse error, or argv path rejection (purity-contract failure).
  3   Schema-enum parse failure from pbir-enhanced-reference.md § 1.

Input shapes
------------
For Phase 0/1 the linter accepts a synthetic *flattened* page JSON for fixture
convenience: a single object with `page`, `width`, `height`, an optional
`_lintConfig`, and a `visuals[]` array (each visual carrying `id`, `position`,
and — for PBIR — `$schema`, `visualType`, `queryState`, `objects`,
`visualContainerObjects`, and an optional `_lintIgnore`).  A real PBIR tree
(`<page>/page.json` + `<page>/visuals/<id>/visual.json`) is the production shape
and is reconciled in a later phase; the flattened shape is what the Table B
fixtures use.

Suppression
-----------
  * `_lintConfig.tolerance.{equal_gap_px,column_align_px}` on the page object
    overrides the default tolerances for checks 3 and 4 (per-page wins over the
    CLI --tolerance-* flags).
  * `_lintIgnore: ["check-3", ...]` on a visual omits that visual from the
    listed checks.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from typing import Literal

# ── Pinned constants ─────────────────────────────────────────────────────────
LINTER_VERSION = "0.1.0"
SCHEMA_VERSION = "1.0.0"  # contract version of the --format=json envelope
PINNED_SCHEMA = "visualContainer/2.7.0"  # PBIR Enhanced schema major this targets

# Hard-coded enum for check-7 page-level displayOption (PascalCase). The
# visualType enum is parsed at runtime from pbir-enhanced-reference.md § 1.
DISPLAY_OPTIONS = frozenset({"FitToPage", "FitToWidth", "ActualSize"})

DEFAULT_GAP_TOLERANCE_PX = 4
DEFAULT_ALIGN_TOLERANCE_PX = 0
DEFAULT_MAX_THEME_OVERRIDES = 12  # check-6 ceiling on objects + visualContainerObjects

# Sanctioned cross-plugin read (see module docstring).
PBIR_REFERENCE_RELPATH = "plugins/power-platform/knowledge/pbir-enhanced-reference.md"

Severity = Literal["info", "warning", "error"]
CheckId = Literal[
    "check-1", "check-2", "check-3", "check-4", "check-5", "check-6", "check-7"
]

CHECK_DEFINITIONS = [
    ("check-1", "No-overlap (AABB)", "All stacks", "error"),
    ("check-2", "Within-canvas", "All stacks", "error"),
    ("check-3", "Equal-gap (horizontal)", "All stacks", "warning"),
    ("check-4", "Column-alignment (vertical)", "All stacks", "warning"),
    ("check-5", "No-empty-binding", "PBIR only", "error"),
    ("check-6", "Theme-compliance (count)", "PBIR only", "warning"),
    ("check-7", "Schema-valid", "PBIR only", "error"),
]


@dataclass(frozen=True)
class Finding:
    check_id: CheckId
    severity: Severity
    page: str  # Page name from page.json or path leaf
    visual_id: str | None  # None for page-level findings (within-canvas check)
    message: str  # Human-readable description
    fix_hint: str  # One-line actionable suggestion


class EnumParseError(Exception):
    """Raised when pbir-enhanced-reference.md § 1 cannot be parsed (exit 3)."""


class InputError(Exception):
    """Raised for I/O, parse, or path-rejection failures (exit 2)."""


# ── Repo-root + path safety ──────────────────────────────────────────────────
def _repo_root() -> str:
    """Resolve the repository root from this file's location.

    lint.py lives at plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py,
    so the repo root is four directories up. No subprocess / git dependency
    (keeps the purity contract: stdlib only, no shelling out).
    """
    here = os.path.abspath(__file__)
    return os.path.abspath(os.path.join(os.path.dirname(here), "..", "..", "..", ".."))


def _resolve_safe(input_path: str) -> str:
    """Reject ".." and paths that resolve outside the repo root; return abspath."""
    if ".." in input_path.split(os.sep):
        raise InputError(f"path component '..' is not allowed: {input_path!r}")
    resolved = os.path.abspath(input_path)
    root = _repo_root()
    if os.path.commonpath([resolved, root]) != root:
        raise InputError(f"path resolves outside repo root: {resolved!r}")
    return resolved


# ── PBIR visualType enum parse (the one sanctioned cross-plugin read) ─────────
def parse_visual_type_enum(reference_path: str | None = None) -> frozenset[str]:
    """Parse the `visualType` enum from pbir-enhanced-reference.md § 1.

    Returns the set of valid visualType strings. Raises EnumParseError (exit 3)
    if § 1 cannot be located or yields no enum.
    """
    path = reference_path or os.path.join(_repo_root(), PBIR_REFERENCE_RELPATH)
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:  # file genuinely absent or unreadable
        raise EnumParseError(f"cannot read PBIR reference {path!r}: {exc}") from exc

    section = re.search(r"## 1\..*?(?=## 2\.)", text, re.DOTALL)
    if not section or "visualType" not in section.group(0):
        raise EnumParseError(f"§ 1 not found or missing 'visualType' in {path!r}")

    body = section.group(0)
    types: set[str] = set()
    # Table rows whose first cell is one or more backtick-wrapped tokens,
    # possibly slash-joined (e.g. `basicShape` / `shape`).
    for first_cell in re.findall(r"^\|\s*([^|]+?)\s*\|", body, re.MULTILINE):
        for token in re.findall(r"`([A-Za-z0-9]+)`", first_cell):
            types.add(token)
    # Drop the table-header literal that names the column.
    types.discard("visualType")
    if not types:
        raise EnumParseError(f"§ 1 parsed but yielded no visualType strings in {path!r}")
    return frozenset(types)


# ── Geometry helpers ─────────────────────────────────────────────────────────
def _pos(visual: dict) -> dict | None:
    p = visual.get("position")
    if not isinstance(p, dict):
        return None
    try:
        return {
            "x": float(p["x"]),
            "y": float(p["y"]),
            "width": float(p["width"]),
            "height": float(p["height"]),
        }
    except (KeyError, TypeError, ValueError):
        return None


def _ignored(visual: dict, check_id: str) -> bool:
    ig = visual.get("_lintIgnore")
    return isinstance(ig, list) and check_id in ig


def _vid(visual: dict, idx: int) -> str:
    return str(visual.get("id") or visual.get("name") or f"visual-{idx}")


# ── Layout-arithmetic checks (stack-agnostic) ────────────────────────────────
def check_no_overlap(page: str, visuals: list[dict]) -> list[Finding]:
    findings: list[Finding] = []
    boxes = []
    for i, v in enumerate(visuals):
        if _ignored(v, "check-1"):
            continue
        p = _pos(v)
        if p:
            boxes.append((_vid(v, i), p))
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            id_a, a = boxes[i]
            id_b, b = boxes[j]
            overlap_x = a["x"] < b["x"] + b["width"] and b["x"] < a["x"] + a["width"]
            overlap_y = a["y"] < b["y"] + b["height"] and b["y"] < a["y"] + a["height"]
            if overlap_x and overlap_y:
                findings.append(
                    Finding(
                        check_id="check-1",
                        severity="error",
                        page=page,
                        visual_id=id_a,
                        message=f"Visual '{id_a}' overlaps visual '{id_b}'.",
                        fix_hint=f"Separate '{id_a}' and '{id_b}' so their bounding boxes do not intersect.",
                    )
                )
    return findings


def check_within_canvas(
    page: str, visuals: list[dict], page_w: float, page_h: float
) -> list[Finding]:
    findings: list[Finding] = []
    for i, v in enumerate(visuals):
        if _ignored(v, "check-2"):
            continue
        p = _pos(v)
        if not p:
            continue
        if (
            p["x"] < 0
            or p["y"] < 0
            or p["x"] + p["width"] > page_w
            or p["y"] + p["height"] > page_h
        ):
            vid = _vid(v, i)
            findings.append(
                Finding(
                    check_id="check-2",
                    severity="error",
                    page=page,
                    visual_id=vid,
                    message=(
                        f"Visual '{vid}' extends outside the {int(page_w)}x{int(page_h)} canvas "
                        f"(x={p['x']:g}, y={p['y']:g}, w={p['width']:g}, h={p['height']:g})."
                    ),
                    fix_hint=f"Move/resize '{vid}' so it stays within 0..{int(page_w)} x 0..{int(page_h)}.",
                )
            )
    return findings


def _rows(boxes: list[tuple[str, dict]], tol: float) -> list[list[tuple[str, dict]]]:
    """Group boxes into rows by y (within tol). Boxes sorted by x inside a row."""
    rows: list[list[tuple[str, dict]]] = []
    for vid, p in sorted(boxes, key=lambda b: (b[1]["y"], b[1]["x"])):
        placed = False
        for row in rows:
            if abs(row[0][1]["y"] - p["y"]) <= tol:
                row.append((vid, p))
                placed = True
                break
        if not placed:
            rows.append([(vid, p)])
    for row in rows:
        row.sort(key=lambda b: b[1]["x"])
    return rows


def check_equal_gap(page: str, visuals: list[dict], tolerance: float) -> list[Finding]:
    """Horizontal gaps between adjacent visuals in a row must be equal (±tol)."""
    findings: list[Finding] = []
    boxes = [
        (_vid(v, i), _pos(v))
        for i, v in enumerate(visuals)
        if _pos(v) and not _ignored(v, "check-3")
    ]
    for row in _rows([(vid, p) for vid, p in boxes], tol=max(tolerance, 1)):
        if len(row) < 3:
            continue  # need >=3 to define >=2 gaps to compare
        gaps = []
        for k in range(len(row) - 1):
            left = row[k][1]
            right = row[k + 1][1]
            gaps.append(right["x"] - (left["x"] + left["width"]))
        if max(gaps) - min(gaps) > tolerance:
            ids = ", ".join(vid for vid, _ in row)
            findings.append(
                Finding(
                    check_id="check-3",
                    severity="warning",
                    page=page,
                    visual_id=row[0][0],
                    message=(
                        f"Unequal horizontal gaps across row [{ids}]: "
                        f"gaps={[round(g, 2) for g in gaps]} px (tolerance ±{tolerance:g}px)."
                    ),
                    fix_hint="Distribute the visuals so adjacent horizontal gaps are equal.",
                )
            )
    return findings


def check_column_alignment(
    page: str, visuals: list[dict], tolerance: float
) -> list[Finding]:
    """Visuals stacked vertically (sharing a column) must share the same x (±tol)."""
    findings: list[Finding] = []
    boxes = [
        (_vid(v, i), _pos(v))
        for i, v in enumerate(visuals)
        if _pos(v) and not _ignored(v, "check-4")
    ]
    rows = _rows([(vid, p) for vid, p in boxes], tol=max(DEFAULT_ALIGN_TOLERANCE_PX, 1))
    if len(rows) < 2:
        return findings  # single row → no columns to compare
    # Column index by ordinal position within each row.
    max_cols = max(len(r) for r in rows)
    for col in range(max_cols):
        xs = [(r[col][0], r[col][1]["x"]) for r in rows if len(r) > col]
        if len(xs) < 2:
            continue
        x_values = [x for _, x in xs]
        if max(x_values) - min(x_values) > tolerance:
            ids = ", ".join(vid for vid, _ in xs)
            findings.append(
                Finding(
                    check_id="check-4",
                    severity="warning",
                    page=page,
                    visual_id=xs[0][0],
                    message=(
                        f"Column {col} not aligned across rows [{ids}]: "
                        f"x values={[round(x, 2) for x in x_values]} (tolerance ±{tolerance:g}px)."
                    ),
                    fix_hint="Align the visuals in this column to a common x coordinate.",
                )
            )
    return findings


# ── PBIR-specific checks ─────────────────────────────────────────────────────
def check_query_state(page: str, visuals: list[dict]) -> list[Finding]:
    """check-5: every populated queryState role must have non-empty projections."""
    findings: list[Finding] = []
    for i, v in enumerate(visuals):
        if _ignored(v, "check-5"):
            continue
        qs = v.get("queryState")
        if not isinstance(qs, dict):
            continue
        vid = _vid(v, i)
        for role, body in qs.items():
            if not isinstance(body, dict):
                continue
            projections = body.get("projections")
            if isinstance(projections, list) and len(projections) == 0:
                findings.append(
                    Finding(
                        check_id="check-5",
                        severity="error",
                        page=page,
                        visual_id=vid,
                        message=f"Visual '{vid}' role '{role}' has an empty projections array.",
                        fix_hint=f"Bind at least one field to '{role}' on '{vid}', or remove the empty role.",
                    )
                )
    return findings


def check_theme_overrides(
    page: str, visuals: list[dict], max_n: int
) -> list[Finding]:
    """check-6: count objects + visualContainerObjects override entries per visual."""
    findings: list[Finding] = []
    for i, v in enumerate(visuals):
        if _ignored(v, "check-6"):
            continue
        objs = v.get("objects") if isinstance(v.get("objects"), dict) else {}
        vco = (
            v.get("visualContainerObjects")
            if isinstance(v.get("visualContainerObjects"), dict)
            else {}
        )
        count = len(objs) + len(vco)
        if count > max_n:
            vid = _vid(v, i)
            findings.append(
                Finding(
                    check_id="check-6",
                    severity="warning",
                    page=page,
                    visual_id=vid,
                    message=(
                        f"Visual '{vid}' has {count} theme-override entries "
                        f"(objects + visualContainerObjects); ceiling is {max_n}."
                    ),
                    fix_hint="Move repeated formatting into the report theme instead of per-visual overrides.",
                )
            )
    return findings


def check_schema(
    page: str,
    visuals: list[dict],
    valid_visual_types: frozenset[str],
    page_display_option: str | None,
) -> list[Finding]:
    """check-7: validate page displayOption enum + each visual's visualType enum."""
    findings: list[Finding] = []
    if page_display_option is not None and page_display_option not in DISPLAY_OPTIONS:
        findings.append(
            Finding(
                check_id="check-7",
                severity="error",
                page=page,
                visual_id=None,
                message=(
                    f"Page displayOption '{page_display_option}' is not one of "
                    f"{sorted(DISPLAY_OPTIONS)}."
                ),
                fix_hint="Set displayOption to one of FitToPage, FitToWidth, ActualSize.",
            )
        )
    for i, v in enumerate(visuals):
        if _ignored(v, "check-7"):
            continue
        vt = v.get("visualType")
        if vt is not None and vt not in valid_visual_types:
            vid = _vid(v, i)
            findings.append(
                Finding(
                    check_id="check-7",
                    severity="error",
                    page=page,
                    visual_id=vid,
                    message=(
                        f"Visual '{vid}' has unknown visualType '{vt}' "
                        "(not in pbir-enhanced-reference.md § 1)."
                    ),
                    fix_hint="Use a visualType listed in pbir-enhanced-reference.md § 1.",
                )
            )
    return findings


# ── Page loading + orchestration ─────────────────────────────────────────────
def _load_page(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as exc:
        raise InputError(f"cannot read input {path!r}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON in {path!r}: {exc}") from exc
    if not isinstance(data, dict):
        raise InputError(f"page JSON must be an object, got {type(data).__name__}")
    return data


def _detect_pbir(page: dict) -> bool:
    if "$schema" in page:
        return True
    for v in page.get("visuals", []):
        if isinstance(v, dict) and "$schema" in v:
            return True
    return False


def lint_page(
    page: dict,
    *,
    page_name: str,
    pbir: bool,
    gap_tolerance: float,
    align_tolerance: float,
    valid_visual_types: frozenset[str],
    max_theme_overrides: int,
) -> list[Finding]:
    visuals = page.get("visuals", [])
    if not isinstance(visuals, list):
        raise InputError("'visuals' must be an array")
    page_w = float(page.get("width", 1280))
    page_h = float(page.get("height", 720))

    cfg = page.get("_lintConfig", {})
    tol = cfg.get("tolerance", {}) if isinstance(cfg, dict) else {}
    if isinstance(tol, dict):
        if "equal_gap_px" in tol:
            gap_tolerance = float(tol["equal_gap_px"])
        if "column_align_px" in tol:
            align_tolerance = float(tol["column_align_px"])

    findings: list[Finding] = []
    findings += check_no_overlap(page_name, visuals)
    findings += check_within_canvas(page_name, visuals, page_w, page_h)
    findings += check_equal_gap(page_name, visuals, gap_tolerance)
    findings += check_column_alignment(page_name, visuals, align_tolerance)

    if pbir:
        findings += check_query_state(page_name, visuals)
        findings += check_theme_overrides(page_name, visuals, max_theme_overrides)
        findings += check_schema(
            page_name,
            visuals,
            valid_visual_types,
            page.get("displayOption"),
        )
    return findings


# ── CLI ──────────────────────────────────────────────────────────────────────
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lint.py",
        description="Layout-arithmetic linter for dashboard/report page definitions.",
    )
    p.add_argument("input_path", nargs="?", help="Page JSON / page dir / fixture dir.")
    p.add_argument("--pbir", action="store_true", help="Force PBIR-specific checks.")
    p.add_argument(
        "--no-pbir", action="store_true", help="Force off PBIR-specific checks."
    )
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.add_argument("--strict", action="store_true", help="Exit nonzero on >= warning.")
    p.add_argument("--tolerance-gap", type=float, default=None, help="check-3 override.")
    p.add_argument(
        "--tolerance-align", type=float, default=None, help="check-4 override."
    )
    p.add_argument("--list-checks", action="store_true", help="Print checks and exit.")
    p.add_argument("--version", action="store_true", help="Print versions and exit.")
    return p


def _print_list_checks() -> None:
    print("Layout-arithmetic linter checks:")
    for cid, name, applies, sev in CHECK_DEFINITIONS:
        print(f"  {cid}  {name:<28} applies-to={applies:<11} default-severity={sev}")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.list_checks:
        _print_list_checks()
        return 0
    if args.version:
        print(f"lint.py {LINTER_VERSION} (schema {PINNED_SCHEMA}, envelope {SCHEMA_VERSION})")
        return 0
    if not args.input_path:
        print("error: input-path is required", file=sys.stderr)
        return 2

    try:
        resolved = _resolve_safe(args.input_path)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    # Determine PBIR mode + load the enum only if PBIR checks may run.
    try:
        page = _load_page(resolved)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.no_pbir:
        pbir = False
    elif args.pbir:
        pbir = True
    else:
        pbir = _detect_pbir(page)

    valid_visual_types: frozenset[str] = frozenset()
    if pbir:
        try:
            valid_visual_types = parse_visual_type_enum()
        except EnumParseError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 3

    gap_tol = args.tolerance_gap if args.tolerance_gap is not None else DEFAULT_GAP_TOLERANCE_PX
    align_tol = (
        args.tolerance_align
        if args.tolerance_align is not None
        else DEFAULT_ALIGN_TOLERANCE_PX
    )
    page_name = str(page.get("page") or os.path.splitext(os.path.basename(resolved))[0])

    try:
        findings = lint_page(
            page,
            page_name=page_name,
            pbir=pbir,
            gap_tolerance=gap_tol,
            align_tolerance=align_tol,
            valid_visual_types=valid_visual_types,
            max_theme_overrides=DEFAULT_MAX_THEME_OVERRIDES,
        )
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    summary = {"info": 0, "warning": 0, "error": 0}
    for f in findings:
        summary[f.severity] += 1

    has_error = summary["error"] > 0
    has_warning = summary["warning"] > 0
    exit_code = 0
    if has_error or (args.strict and has_warning):
        exit_code = 1

    if args.format == "json":
        envelope = {
            "schema_version": SCHEMA_VERSION,
            "linter_version": LINTER_VERSION,
            "input_path": resolved,
            "exit_code": exit_code,
            "summary": summary,
            "findings": [asdict(f) for f in findings],
        }
        print(json.dumps(envelope, indent=2))
    else:
        if not findings:
            mode = "PBIR" if pbir else "non-PBIR"
            print(f"OK — {page_name} ({mode}): no findings.")
        else:
            for f in findings:
                where = f"{f.page}/{f.visual_id}" if f.visual_id else f.page
                print(f"[{f.severity}] {f.check_id} {where}: {f.message}")
                print(f"    fix: {f.fix_hint}")
        if not pbir:
            print("info: PBIR-specific checks (5,6,7) skipped (non-PBIR input).")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
