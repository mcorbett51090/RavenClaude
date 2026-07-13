#!/usr/bin/env python3
"""check-brand-a11y.py - a zero-dependency WCAG contrast-pair checker for a brand palette.

Makes the brand book's WCAG contrast gate mechanical: "does this brand's text-on-background
role pair pass AA?" becomes a computation, not a guess by eye. It MIRRORS the WCAG 2.x math in
web-design/scripts/contrast_ratio.py so the WCAG-pair gate is runnable WITHOUT a hard web-design
dependency; for a full design-system contrast audit at token-build time, defer to that script
(invoked through the web-design:design-tokens-scaffolding delegation).

This checker is brand-ROLE-aware: it validates the specific role pairs a brand book must carry
(text-on-background, accent-on-surface, UI/focus), so a failing PRIMARY text pair fails the
handoff. Two modes:

  pair    Given a foreground + background hex, report the contrast ratio and pass/fail against
          the WCAG threshold for normal text, large text (>=18pt / 14pt bold), or UI/graphical
          objects (SC 1.4.3 + SC 1.4.11). Exits non-zero if the requested level/size fails.

  check   Read a brand-palette JSON of {role: {fg, bg, size?, level?}} pairs and report a table;
          exits non-zero if any pair fails its declared bar (the brand-book contrast gate).

This is a CHECKER, not a renderer - supply the ACTUAL displayed colors (measure against the real
background a surface renders on, gradients/overlays flattened, every interactive state). A passing
nominal ratio measured against the wrong background is not a pass. Stdlib only (argparse, json);
runs anywhere Python 3.8+ is present.

The math (WCAG 2.x relative luminance + contrast ratio), verified 2026-07-13 against W3C WCAG
techniques (https://www.w3.org/TR/WCAG20-TECHS/G18.html) and the WCAG 2.2 understanding docs
(https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html):

  - sRGB channel c in [0,1]: linear = c/12.92 if c <= 0.03928 else ((c + 0.055)/1.055) ** 2.4
  - relative luminance L = 0.2126*R + 0.7152*G + 0.0722*B (linearized channels)
  - contrast ratio = (Llighter + 0.05) / (Ldarker + 0.05), range 1:1 .. 21:1

Thresholds (SC 1.4.3 / SC 1.4.6 / SC 1.4.11), [verify-at-use] - re-confirm the WCAG version at use:
  - normal text:  AA 4.5:1, AAA 7:1
  - large text:   AA 3:1,   AAA 4.5:1  (>= 18pt, or >= 14pt bold)
  - ui/graphical: 3:1 (SC 1.4.11; AA - no separate AAA bar)

Examples
--------
  # A single brand text pair, normal text, AA (the default)
  python3 check-brand-a11y.py pair --fg "#1a1a2e" --bg "#ffffff"

  # Validate a brand palette's role pairs (the brand-book gate)
  python3 check-brand-a11y.py check --palette brand-pairs.json
"""

from __future__ import annotations

import argparse
import json
import sys

# (AA, AAA) minimum contrast per text size. "ui" has only a 3:1 AA bar.
# [verify-at-use] - WCAG SC 1.4.3 / 1.4.6 / 1.4.11.
THRESHOLDS = {
    "normal": {"AA": 4.5, "AAA": 7.0},
    "large": {"AA": 3.0, "AAA": 4.5},
    "ui": {"AA": 3.0, "AAA": 3.0},
}


def _parse_hex(value: str) -> tuple[float, float, float]:
    """Parse '#rgb' / '#rrggbb' (with or without '#') into 0..1 sRGB channels."""
    s = value.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"not a 3- or 6-digit hex color: {value!r}")
    try:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
    except ValueError as exc:
        raise ValueError(f"not a hex color: {value!r}") from exc
    return r / 255.0, g / 255.0, b / 255.0


def _linearize(c: float) -> float:
    """sRGB gamma-expansion of one 0..1 channel (WCAG relative-luminance step)."""
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    """WCAG relative luminance L of an sRGB hex color (0..1)."""
    r, g, b = (_linearize(c) for c in _parse_hex(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    """WCAG contrast ratio between two hex colors (1.0 .. 21.0)."""
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    lighter, darker = (l1, l2) if l1 >= l2 else (l2, l1)
    return (lighter + 0.05) / (darker + 0.05)


def required_ratio(size: str, level: str) -> float:
    """The minimum contrast ratio for a given text size + conformance level."""
    return THRESHOLDS[size][level]


def cmd_pair(args: argparse.Namespace) -> int:
    """Single fg/bg check. Exit 1 if it fails the requested size+level bar."""
    try:
        ratio = contrast_ratio(args.fg, args.bg)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    needed = required_ratio(args.size, args.level)
    ok = ratio >= needed
    print(f"foreground : {args.fg}")
    print(f"background : {args.bg}")
    print(f"ratio      : {ratio:.2f}:1")
    print(f"required   : {needed:.1f}:1  ({args.size} text, WCAG {args.level})")
    print(f"status     : {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(
            "\nFix the palette at the ROLE level, not the component. Measure against the ACTUAL "
            "rendered background (gradients/overlays flattened) and every interactive state. A "
            "failing primary text pair fails the brand handoff.",
            file=sys.stderr,
        )
    return 0 if ok else 1


def cmd_check(args: argparse.Namespace) -> int:
    """Batch check a brand-palette JSON of role pairs. Exit 1 if any pair fails its bar."""
    try:
        with open(args.palette, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: could not read --palette: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("error: --palette must be an object {role: {fg, bg, ...}}", file=sys.stderr)
        return 2

    fails = 0
    print(f"{'role':<24} {'ratio':>8} {'need':>6} {'size':<8} {'lvl':<4} status")
    print("-" * 64)
    for role, spec in data.items():
        try:
            fg = spec["fg"]
            bg = spec["bg"]
            size = spec.get("size", "normal")
            level = spec.get("level", "AA")
            if size not in THRESHOLDS or level not in ("AA", "AAA"):
                raise ValueError("size must be normal|large|ui, level AA|AAA")
            ratio = contrast_ratio(fg, bg)
        except (KeyError, TypeError, ValueError) as exc:
            print(f"error: role {role!r} is malformed ({exc})", file=sys.stderr)
            return 2
        needed = required_ratio(size, level)
        ok = ratio >= needed
        if not ok:
            fails += 1
        status = "PASS" if ok else "FAIL"
        print(f"{role:<24} {ratio:>7.2f}: {needed:>5.1f} {size:<8} {level:<4} {status}")
    print("-" * 64)
    if fails:
        print(
            f"\n{fails} brand role pair(s) fail their declared WCAG bar - the palette is NOT "
            "ready for handoff. Fix at the role and re-run."
        )
    else:
        print("\nAll brand role pairs pass their declared WCAG bar - palette gate satisfied.")
    return 1 if fails else 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="check-brand-a11y.py",
        description="WCAG contrast-pair checker for a brand palette (single pair or role batch).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pp = sub.add_parser("pair", help="Check one foreground/background pair.")
    pp.add_argument("--fg", required=True, help="Foreground (text) hex color.")
    pp.add_argument("--bg", required=True, help="Background hex color (the REAL one).")
    pp.add_argument(
        "--size",
        choices=["normal", "large", "ui"],
        default="normal",
        help="normal text (default), large text (>=18pt / 14pt bold), or ui/graphical.",
    )
    pp.add_argument(
        "--level",
        choices=["AA", "AAA"],
        default="AA",
        help="WCAG conformance level (default AA).",
    )
    pp.set_defaults(func=cmd_pair)

    pc = sub.add_parser("check", help="Batch-check brand role pairs from a palette JSON.")
    pc.add_argument(
        "--palette",
        required=True,
        help="JSON object {role: {fg, bg, size?, level?}} of brand role pairs.",
    )
    pc.set_defaults(func=cmd_check)

    return parser


def main(argv: list | None = None) -> int:
    """Entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
