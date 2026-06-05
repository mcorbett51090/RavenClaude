#!/usr/bin/env python3
"""contrast_ratio.py - a zero-dependency WCAG color-contrast checker.

Makes the WCAG 2.x / 2.2 contrast-ratio arithmetic mechanical and CI-gateable
so "does this text pass AA?" is a computation, not a guess by eye. Two modes:

  pair      Given a foreground and a background color (hex), report the contrast
            ratio and pass/fail against the WCAG thresholds for normal text,
            large text, and UI components / graphical objects (SC 1.4.3 +
            SC 1.4.11). Exits non-zero if the requested level/size fails - so
            it can gate a PR or a token review.

  check     Read a JSON file of {name: {fg, bg, size, level}} token/usage pairs
            and report a table; exits non-zero if any fails its declared bar.
            Use it to assert a design system's text/surface pairings stay
            within contrast as tokens change (the token-drift guard).

This is a CHECKER, not a renderer - you supply the ACTUAL displayed colors
(measure against the real background a surface renders on, including gradients
and overlays resolved to a flat color; check every interactive state). A
passing nominal ratio measured against the wrong background is not a pass - see
the wcag-contrast-and-focus-order-audit scenario. Stdlib only (argparse, json);
runs anywhere Python 3.8+ is present.

The math (WCAG 2.x relative luminance + contrast ratio), verified 2026-06-05
against W3C WCAG techniques (https://www.w3.org/TR/WCAG20-TECHS/G18.html) and
the WCAG 2.2 understanding docs
(https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html):

  - sRGB channel c in [0,1]: linear = c/12.92 if c <= 0.03928
    else ((c + 0.055)/1.055) ** 2.4
  - relative luminance L = 0.2126*R + 0.7152*G + 0.0722*B (linearized channels)
  - contrast ratio = (Llighter + 0.05) / (Ldarker + 0.05), range 1:1 .. 21:1

Thresholds (SC 1.4.3 Contrast Minimum / SC 1.4.6 Enhanced / SC 1.4.11
Non-text Contrast), [verify-at-use] - re-confirm the WCAG version at use:
  - normal text:  AA 4.5:1, AAA 7:1
  - large text:   AA 3:1,   AAA 4.5:1  (>= 18pt, or >= 14pt bold)
  - ui/graphical: 3:1 (SC 1.4.11; AA - no separate AAA bar)

Examples
--------
  # A single pair, normal text, AA (the default)
  python3 contrast_ratio.py pair --fg "#6b7280" --bg "#ffffff"

  # Large-text AAA
  python3 contrast_ratio.py pair --fg "#767676" --bg "#fff" --size large --level AAA

  # Assert a set of token pairings stays in contrast
  python3 contrast_ratio.py check --from-json pairs.json
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
            "\nMeasure against the ACTUAL rendered background (gradients/overlays "
            "flattened) and every interactive state; fix at the token, not the "
            "component - see the wcag-contrast-and-focus-order-audit scenario.",
            file=sys.stderr,
        )
    return 0 if ok else 1


def cmd_check(args: argparse.Namespace) -> int:
    """Batch check from JSON. Exit 1 if any pairing fails its declared bar."""
    try:
        with open(args.from_json, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: could not read --from-json: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("error: --from-json must be an object {name: {fg, bg, ...}}", file=sys.stderr)
        return 2

    fails = 0
    print(f"{'name':<24} {'ratio':>8} {'need':>6} {'size':<8} {'lvl':<4} status")
    print("-" * 64)
    for name, spec in data.items():
        try:
            fg = spec["fg"]
            bg = spec["bg"]
            size = spec.get("size", "normal")
            level = spec.get("level", "AA")
            if size not in THRESHOLDS or level not in ("AA", "AAA"):
                raise ValueError("size must be normal|large|ui, level AA|AAA")
            ratio = contrast_ratio(fg, bg)
        except (KeyError, TypeError, ValueError) as exc:
            print(f"error: pairing {name!r} is malformed ({exc})", file=sys.stderr)
            return 2
        needed = required_ratio(size, level)
        ok = ratio >= needed
        if not ok:
            fails += 1
        status = "PASS" if ok else "FAIL"
        print(f"{name:<24} {ratio:>7.2f}: {needed:>5.1f} {size:<8} {level:<4} {status}")
    print("-" * 64)
    if fails:
        print(f"\n{fails} pairing(s) fail their declared contrast bar - failing.")
    else:
        print("\nAll pairings pass their declared contrast bar.")
    return 1 if fails else 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="contrast_ratio.py",
        description="WCAG color-contrast checker (single pair or batch).",
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

    pc = sub.add_parser("check", help="Batch-check token pairings from JSON.")
    pc.add_argument(
        "--from-json",
        required=True,
        help='JSON object {name: {fg, bg, size?, level?}}.',
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
