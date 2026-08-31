#!/usr/bin/env python3
"""check-design-schema.py — the single stdlib conformance point for design-schema.json.

WHY THIS EXISTS. `schemas/design-schema.schema.json` (draft-07) documents the shape of
the design-clone skill's capture contract, but `.github/workflows/validate-schemas.yml`
validates only `plugin.json`/`marketplace.json` — it never touches this artifact. And
the repo ships no `jsonschema` dependency (stdlib-only is a hard constraint here). So
there is exactly ONE place instance-conformance is checked: this script, hand-rolled in
the `check-frontmatter.py` convention (structural asserts, not a generic schema
interpreter). It is the single point BOTH the static extractor's output (P2) and the
apply-path's report (P3) are validated against — neither skill re-implements this logic
or imports across skill boundaries.

THE HONESTY PIVOT. `capture_method` appears both document-level and per-dimension
(spacing/type_scale/grid/elevation each carry their own). The document-level value is
the CEILING of what a given extraction pass could produce: v1 ships only a "static"
producer (declared-CSS parsing via stdlib — no browser CSSOM, so it structurally cannot
read a rendered/computed style). A document declared "static" can therefore never
honestly contain a dimension claiming "computed" — that would assert a browser-rendered
value came out of a pass that has no browser. This script enforces that as a real
structural check (`_provenance_violations`), not a decorative field nobody reads.

Usage:
    check-design-schema.py <path/to/design-schema.json>   # validate one instance
    check-design-schema.py --self-test                    # embedded good/bad fixtures
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

_CAPTURE_METHODS = ("static", "computed")
_IDENTITY_ACTIONS = ("swap", "omit", "human-decision")

_TOP_REQUIRED = (
    "source",
    "capture_method",
    "spacing",
    "type_scale",
    "grid",
    "elevation",
    "components",
    "identity_flags",
    "confidence_notes",
)

# The four dimensions that self-declare a per-dimension capture_method. components /
# identity_flags / confidence_notes do not carry one (see schema doc).
_DIMENSION_KEYS = ("spacing", "type_scale", "grid", "elevation")


def _is_str(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _is_num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _is_num_or_null(v: Any) -> bool:
    return v is None or _is_num(v)


def _is_int_or_null(v: Any) -> bool:
    return v is None or (isinstance(v, int) and not isinstance(v, bool))


def _is_list(v: Any) -> bool:
    return isinstance(v, list)


def _check_capture_method(field: str, value: Any) -> list[str]:
    if value not in _CAPTURE_METHODS:
        return [f"'{field}' must be one of {_CAPTURE_METHODS!r}, got {value!r}"]
    return []


def _check_source(source: Any) -> list[str]:
    if not isinstance(source, dict):
        return ["'source' must be an object with 'url' and 'fetched_at'"]
    errs: list[str] = []
    if not _is_str(source.get("url")):
        errs.append("'source.url' is missing or not a non-empty string")
    if not _is_str(source.get("fetched_at")):
        errs.append(
            "'source.fetched_at' is missing or not a non-empty string (UTC ISO-8601 timestamp)"
        )
    if "title" in source and source["title"] is not None and not isinstance(source["title"], str):
        errs.append("'source.title' must be a string when present")
    return errs


def _check_spacing(spacing: Any) -> list[str]:
    if not isinstance(spacing, dict):
        return ["'spacing' must be an object"]
    errs: list[str] = []
    if "scale" not in spacing:
        errs.append(
            "'spacing.scale' is required (the derived spacing scale; may be an empty "
            "array on honest degrade, but the key itself must be present)"
        )
    elif not _is_list(spacing["scale"]):
        errs.append("'spacing.scale' must be an array")
    elif not all(_is_num(v) for v in spacing["scale"]):
        errs.append("'spacing.scale' items must all be numbers")
    if "base_unit" in spacing and not _is_int_or_null(spacing["base_unit"]):
        errs.append("'spacing.base_unit' must be an integer or null")
    if "capture_method" not in spacing:
        errs.append("'spacing.capture_method' is required")
    else:
        errs += _check_capture_method("spacing.capture_method", spacing["capture_method"])
    return errs


def _check_type_scale(type_scale: Any) -> list[str]:
    if not isinstance(type_scale, dict):
        return ["'type_scale' must be an object"]
    errs: list[str] = []
    if "sizes" not in type_scale:
        errs.append(
            "'type_scale.sizes' is required (the derived font-size scale; may be an "
            "empty array on honest degrade, but the key itself must be present)"
        )
    elif not _is_list(type_scale["sizes"]):
        errs.append("'type_scale.sizes' must be an array")
    elif not all(_is_num(v) for v in type_scale["sizes"]):
        errs.append("'type_scale.sizes' items must all be numbers")
    if "base_size" in type_scale and not _is_num_or_null(type_scale["base_size"]):
        errs.append("'type_scale.base_size' must be a number or null")
    if "ratio" in type_scale and not _is_num_or_null(type_scale["ratio"]):
        errs.append("'type_scale.ratio' must be a number or null")
    if "capture_method" not in type_scale:
        errs.append("'type_scale.capture_method' is required")
    else:
        errs += _check_capture_method("type_scale.capture_method", type_scale["capture_method"])
    return errs


def _check_grid(grid: Any) -> list[str]:
    if not isinstance(grid, dict):
        return ["'grid' must be an object"]
    errs: list[str] = []
    if "breakpoints" not in grid:
        errs.append(
            "'grid.breakpoints' is required (may be an empty array on honest degrade, "
            "but the key itself must be present)"
        )
    elif not _is_list(grid["breakpoints"]):
        errs.append("'grid.breakpoints' must be an array")
    elif not all(_is_num(v) or _is_str(v) for v in grid["breakpoints"]):
        errs.append(
            "'grid.breakpoints' items must all be strings or numbers (raw declared "
            "@media values)"
        )
    if "columns" in grid and not _is_int_or_null(grid["columns"]):
        errs.append("'grid.columns' must be an integer or null")
    if "gutter" in grid and grid["gutter"] is not None and not isinstance(grid["gutter"], str):
        errs.append("'grid.gutter' must be a string or null")
    if (
        "container_max" in grid
        and grid["container_max"] is not None
        and not isinstance(grid["container_max"], str)
    ):
        errs.append("'grid.container_max' must be a string or null")
    if "capture_method" not in grid:
        errs.append("'grid.capture_method' is required")
    else:
        errs += _check_capture_method("grid.capture_method", grid["capture_method"])
    return errs


def _check_elevation(elevation: Any) -> list[str]:
    if not isinstance(elevation, dict):
        return ["'elevation' must be an object"]
    errs: list[str] = []
    if "shadows" not in elevation:
        errs.append(
            "'elevation.shadows' is required (may be an empty array on honest degrade, "
            "but the key itself must be present)"
        )
    elif not _is_list(elevation["shadows"]):
        errs.append(
            "'elevation.shadows' must be an array (got "
            f"{type(elevation['shadows']).__name__})"
        )
    elif not all(_is_str(v) for v in elevation["shadows"]):
        errs.append(
            "'elevation.shadows' items must all be non-empty strings (raw box-shadow "
            "declarations)"
        )
    if "capture_method" not in elevation:
        errs.append("'elevation.capture_method' is required")
    else:
        errs += _check_capture_method("elevation.capture_method", elevation["capture_method"])
    return errs


def _check_components(components: Any) -> list[str]:
    if not _is_list(components):
        return ["'components' must be an array"]
    errs: list[str] = []
    for i, c in enumerate(components):
        prefix = f"components[{i}]"
        if not isinstance(c, dict):
            errs.append(f"'{prefix}' must be an object")
            continue
        if not _is_str(c.get("name")):
            errs.append(f"'{prefix}.name' is missing or not a non-empty string")
        if "anatomy" in c and not _is_list(c["anatomy"]):
            errs.append(f"'{prefix}.anatomy' must be an array when present")
        if "recipe" in c and not isinstance(c["recipe"], dict):
            errs.append(f"'{prefix}.recipe' must be an object when present")
    return errs


def _check_identity_flags(flags: Any) -> list[str]:
    if not _is_list(flags):
        return ["'identity_flags' must be an array"]
    errs: list[str] = []
    for i, f in enumerate(flags):
        prefix = f"identity_flags[{i}]"
        if not isinstance(f, dict):
            errs.append(f"'{prefix}' must be an object")
            continue
        if not _is_str(f.get("kind")):
            errs.append(f"'{prefix}.kind' is missing or not a non-empty string")
        if not _is_str(f.get("evidence")):
            errs.append(f"'{prefix}.evidence' is missing or not a non-empty string")
        action = f.get("action")
        if action not in _IDENTITY_ACTIONS:
            errs.append(
                f"'{prefix}.action' must be one of {_IDENTITY_ACTIONS!r}, got {action!r}"
            )
    return errs


def _check_confidence_notes(notes: Any) -> list[str]:
    if not _is_list(notes):
        return ["'confidence_notes' must be an array"]
    if not all(isinstance(n, str) for n in notes):
        return ["'confidence_notes' items must all be strings"]
    return []


def _provenance_violations(data: dict) -> list[str]:
    """The honesty pivot: no per-dimension capture_method may exceed the document-level
    ceiling. v1's only producer is "static", which has no browser CSSOM access, so a
    "static" document can never honestly carry a "computed" dimension."""
    errs: list[str] = []
    doc_method = data.get("capture_method")
    if doc_method != "static":
        return errs
    for dim in _DIMENSION_KEYS:
        dim_value = data.get(dim)
        if not isinstance(dim_value, dict):
            continue
        dim_method = dim_value.get("capture_method")
        if dim_method == "computed":
            errs.append(
                f"'{dim}.capture_method' is 'computed' but the document-level "
                "'capture_method' is 'static' — a static extraction pass has no browser "
                "CSSOM access and cannot honestly produce a computed value "
                "(provenance-honesty violation)"
            )
    return errs


def violations(data: Any) -> list[str]:
    """Return every conformance problem in `data` as a specific, named error string.
    Empty list means the instance conforms."""
    if not isinstance(data, dict):
        return ["document root must be a JSON object"]

    errs: list[str] = []
    for key in _TOP_REQUIRED:
        if key not in data:
            errs.append(f"'{key}' is required at the document root")

    if "source" in data:
        errs += _check_source(data["source"])
    if "capture_method" in data:
        errs += _check_capture_method("capture_method", data["capture_method"])
    if "spacing" in data:
        errs += _check_spacing(data["spacing"])
    if "type_scale" in data:
        errs += _check_type_scale(data["type_scale"])
    if "grid" in data:
        errs += _check_grid(data["grid"])
    if "elevation" in data:
        errs += _check_elevation(data["elevation"])
    if "components" in data:
        errs += _check_components(data["components"])
    if "identity_flags" in data:
        errs += _check_identity_flags(data["identity_flags"])
    if "confidence_notes" in data:
        errs += _check_confidence_notes(data["confidence_notes"])

    if (
        "brand_kit_ref" in data
        and data["brand_kit_ref"] is not None
        and not isinstance(data["brand_kit_ref"], str)
    ):
        errs.append("'brand_kit_ref' must be a string or null when present")

    errs += _provenance_violations(data)
    return errs


def _good_instance() -> dict[str, Any]:
    """A minimal-but-complete valid design-schema instance, embedded so --self-test
    never depends on tests/fixtures/ existing on disk."""
    return {
        "$schema": "https://github.com/mcorbett51090/RavenClaude/schemas/design-schema.schema.json",
        "source": {
            "url": "https://example.com",
            "fetched_at": "2026-08-13T00:00:00Z",
            "title": "Example Co.",
        },
        "capture_method": "static",
        "spacing": {"base_unit": 8, "scale": [4, 8, 16, 24], "capture_method": "static"},
        "type_scale": {
            "base_size": 16,
            "ratio": 1.25,
            "sizes": [12, 14, 16, 20],
            "capture_method": "static",
        },
        "grid": {
            "breakpoints": ["640px", "1024px"],
            "columns": 12,
            "gutter": "24px",
            "container_max": "1200px",
            "capture_method": "static",
        },
        "elevation": {
            "shadows": ["0 1px 2px rgba(0,0,0,0.05)", "0 2px 8px rgba(0,0,0,0.1)"],
            "capture_method": "static",
        },
        "components": [
            {"name": "button", "anatomy": ["label"], "recipe": {"padding": "8px 16px"}},
        ],
        "brand_kit_ref": None,
        "identity_flags": [
            {
                "kind": "logo",
                "evidence": "img[alt~=logo] found in header region",
                "action": "human-decision",
            }
        ],
        "confidence_notes": ["spacing.base_unit fit at residual 0.02 for base 8 vs 0.31 for base 4"],
    }


def _self_test() -> int:
    good = _good_instance()

    missing_scale = copy.deepcopy(good)
    del missing_scale["spacing"]["scale"]

    shadow_not_array = copy.deepcopy(good)
    shadow_not_array["elevation"]["shadows"] = "0 1px 2px rgba(0,0,0,0.05)"

    dishonest_capture_method = copy.deepcopy(good)
    dishonest_capture_method["spacing"]["capture_method"] = "computed"

    missing_top_level = copy.deepcopy(good)
    del missing_top_level["identity_flags"]

    bad_action_enum = copy.deepcopy(good)
    bad_action_enum["identity_flags"][0]["action"] = "auto-approve"

    good_cases = [("fully valid instance", good)]
    bad_cases = [
        ("missing spacing.scale", missing_scale, "spacing.scale"),
        ("elevation.shadows not an array", shadow_not_array, "elevation.shadows"),
        (
            "static document with a computed dimension (dishonest provenance)",
            dishonest_capture_method,
            "provenance-honesty",
        ),
        ("missing required top-level identity_flags", missing_top_level, "identity_flags"),
        ("identity_flags[].action outside the enum", bad_action_enum, "action"),
    ]

    ok = True
    print("check-design-schema.py self-test")
    for label, inst in good_cases:
        errs = violations(inst)
        passed = not errs
        ok = ok and passed
        print(f"  [{'OK' if passed else 'FAIL'}] good: {label}" + ("" if passed else f" -> unexpectedly rejected: {errs!r}"))

    for label, inst, must_mention in bad_cases:
        errs = violations(inst)
        hit = any(must_mention in e for e in errs)
        passed = bool(errs) and hit
        ok = ok and passed
        detail = "" if passed else f" -> expected an error naming '{must_mention}', got {errs!r}"
        print(f"  [{'OK' if passed else 'FAIL'}] bad:  {label}{detail}")

    if ok:
        print(
            "\nself-test passed (the good instance is accepted; every bad instance is "
            "rejected with a specific named error)"
        )
        return 0
    print("\nself-test FAILED — the checker does not have the teeth it claims")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("path", nargs="?", help="path to a design-schema.json instance to validate")
    ap.add_argument(
        "--self-test", action="store_true", help="run the embedded good/bad fixtures and exit"
    )
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    if not args.path:
        ap.error("a PATH is required unless --self-test is given")

    p = Path(args.path)
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"✗ cannot read {p}: {exc}")
        return 1
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"✗ {p}: invalid JSON — {exc}")
        return 1

    errs = violations(data)
    if errs:
        print(f"✗ {p}: design-schema conformance FAILED ({len(errs)} finding(s)):")
        for e in errs:
            print(f"  - {e}")
        return 1
    print(f"✓ {p}: valid design-schema instance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
