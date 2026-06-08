#!/usr/bin/env python3
"""accessibility_calc.py — a zero-dependency Accessibility Engineering decision calculator.

Removes arithmetic error from 3 recurring accessibility engineering decisions:

  conformance   Weighted conformance score from issue counts by severity/level.

  remediation   Rank issues by user-impact over effort.

  contrast      WCAG contrast ratio from hex foreground/background.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No user PII belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No user PII."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_conformance(a):
    if a.criteria_tested <= 0:
        print("error: --criteria-tested must be > 0", file=sys.stderr)
        return 2
    for n, v in [("critical", a.critical), ("serious", a.serious), ("moderate", a.moderate), ("minor", a.minor)]:
        if v < 0:
            print(f"error: --{n} must be >= 0", file=sys.stderr)
            return 2
    weighted_issues = a.critical * 10 + a.serious * 5 + a.moderate * 2 + a.minor * 1
    max_weight = a.criteria_tested * 10
    score = max(0.0, 1.0 - weighted_issues / max_weight)
    print("=== WCAG conformance score (CLAUDE.md S3 #1/#2) ===")
    print(f"  Criteria tested     : {a.criteria_tested:g}")
    print(f"  Critical (Level-A)  : {a.critical:g}  (weight 10)")
    print(f"  Serious             : {a.serious:g}  (weight 5)")
    print(f"  Moderate            : {a.moderate:g}  (weight 2)")
    print(f"  Minor               : {a.minor:g}  (weight 1)")
    print(f"  Weighted issue load : {weighted_issues:g} of max {max_weight:g}")
    print(f"  >> Weighted conformance score: {_pct(score)}")
    if a.critical > 0:
        print(f"  >> NOT CONFORMANT: {a.critical:g} Level-A blocker(s) fail the page at every level (S3 #2) — fix FIRST")
    else:
        print("  >> No Level-A blockers; rank remaining issues by impact (S3 #7)")
    print("  NOTE: a score from an automated scan alone is a floor, not a conformance claim (S3 #2).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_remediation(a):
    if a.effort <= 0:
        print("error: --effort must be > 0", file=sys.stderr)
        return 2
    if not (1 <= a.user_impact <= 10):
        print("error: --user-impact must be in [1,10]", file=sys.stderr)
        return 2
    if not (0 < a.users_affected <= 1):
        print("error: 0 < --users-affected <= 1", file=sys.stderr)
        return 2
    priority = (a.user_impact * a.users_affected) / a.effort
    print("=== Remediation priority (CLAUDE.md S3 #7) ===")
    print(f"  User-impact (1-10)  : {a.user_impact:g}")
    print(f"  Users affected      : {_pct(a.users_affected)}")
    print(f"  Effort (person-days): {a.effort:g}")
    print(f"  >> Priority score   : {priority:.2f}  (impact x users / effort)")
    if priority >= 2.0:
        print("  >> HIGH priority — high-impact quick win, do early (S3 #7)")
    elif priority >= 0.5:
        print("  >> MEDIUM priority — schedule in the remediation roadmap")
    else:
        print("  >> LOW priority — defer/batch unless it is a Level-A blocker (S3 #2)")
    print("  NOTE: Level-A blockers lead regardless of this score — they fail the page (S3 #2).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_contrast(a):
    def _parse_hex(s):
        h = s.strip().lstrip('#')
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        if len(h) != 6:
            return None
        try:
            return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return None
    fg = _parse_hex(a.fg)
    bg = _parse_hex(a.bg)
    if fg is None or bg is None:
        print("error: --fg and --bg must be hex like #767676, 767676, or #abc", file=sys.stderr)
        return 2
    def _rel_lum(rgb):
        chans = []
        for v in rgb:
            c = v / 255.0
            c = c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
            chans.append(c)
        return 0.2126 * chans[0] + 0.7152 * chans[1] + 0.0722 * chans[2]
    l_fg = _rel_lum(fg)
    l_bg = _rel_lum(bg)
    l_light = max(l_fg, l_bg)
    l_dark = min(l_fg, l_bg)
    ratio = (l_light + 0.05) / (l_dark + 0.05)
    print("=== WCAG contrast ratio (CLAUDE.md S3 #5) ===")
    print(f"  Foreground          : #{fg[0]:02x}{fg[1]:02x}{fg[2]:02x}  (luminance {l_fg:.4f})")
    print(f"  Background          : #{bg[0]:02x}{bg[1]:02x}{bg[2]:02x}  (luminance {l_bg:.4f})")
    print(f"  >> Contrast ratio   : {ratio:.2f}:1")
    print("  --- WCAG thresholds ---")
    print(f"  AA  normal (>=4.5)  : {'PASS' if ratio >= 4.5 else 'FAIL'}")
    print(f"  AA  large  (>=3.0)  : {'PASS' if ratio >= 3.0 else 'FAIL'}")
    print(f"  AAA normal (>=7.0)  : {'PASS' if ratio >= 7.0 else 'FAIL'}")
    print(f"  AAA large  (>=4.5)  : {'PASS' if ratio >= 4.5 else 'FAIL'}")
    print("  NOTE: large text = >=18pt (24px) or >=14pt (18.66px) bold; compute, don't eyeball (S3 #5).")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='accessibility_calc.py',
        description="Accessibility Engineering decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('conformance', help='weighted conformance score + critical-blocker flag')
    sp.add_argument('--critical', type=float, default=0.0, help='count of critical (Level-A blocker) issues')
    sp.add_argument('--serious', type=float, default=0.0, help='count of serious issues')
    sp.add_argument('--moderate', type=float, default=0.0, help='count of moderate issues')
    sp.add_argument('--minor', type=float, default=0.0, help='count of minor issues')
    sp.add_argument('--criteria-tested', type=float, required=True, help='number of success criteria tested')
    sp.set_defaults(func=cmd_conformance)

    sp = sub.add_parser('remediation', help='priority = user-impact / effort, with effort-impact framing')
    sp.add_argument('--user-impact', type=float, required=True, help='user-impact score (1-10)')
    sp.add_argument('--effort', type=float, required=True, help='effort score in person-days')
    sp.add_argument('--users-affected', type=float, default=1.0, help='share of users affected (0-1)')
    sp.set_defaults(func=cmd_remediation)

    sp = sub.add_parser('contrast', help='relative-luminance contrast ratio + AA/AAA pass for normal & large text')
    sp.add_argument('--fg', type=str, required=True, help='foreground color hex (e.g. #767676 or 767676)')
    sp.add_argument('--bg', type=str, required=True, help='background color hex (e.g. #ffffff or ffffff)')
    sp.set_defaults(func=cmd_contrast)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
