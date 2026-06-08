#!/usr/bin/env python3
"""k12_school_administration_calc.py — a zero-dependency K-12 School Administration decision calculator.

Removes arithmetic error from 3 recurring k-12 school administration decisions:

  enrollment-fundingFunding from enrollment x per-pupil x ADA + per-attendance-point value.

  staffing-ratioTeachers needed + salary cost + variance vs current.

  absenteeism   Chronic-absentee rate, flag, and recovery funding upside.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No student PII (FERPA) belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No student PII (FERPA)."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_enrollment_funding(a):
    if a.enrollment <= 0 or a.per_pupil_funding < 0:
        print("error: --enrollment > 0 and --per-pupil-funding >= 0", file=sys.stderr)
        return 2
    if not (0 < a.ada_rate <= 1):
        print("error: 0 < --ada-rate <= 1", file=sys.stderr)
        return 2
    gross_funding = a.enrollment * a.per_pupil_funding
    funding = gross_funding * a.ada_rate
    per_point = gross_funding * 0.01
    print("=== Enrollment funding (CLAUDE.md S3 #1/#2) ===")
    print(f"  Enrollment           : {a.enrollment:g}")
    print(f"  Per-pupil funding    : {_money(a.per_pupil_funding)}  (source + date it, S3 #8)")
    print(f"  ADA rate             : {_pct(a.ada_rate)}")
    print(f"  Enrollment-based funding : {_money(gross_funding)}")
    print(f"  >> ADA-adjusted funding  : {_money(funding)}")
    print(f"  >> Each attendance point worth: {_money(per_point)}  (1% of ADA — the dual lever, S3 #2)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_staffing_ratio(a):
    if a.enrollment <= 0 or a.target_ratio <= 0 or a.avg_teacher_cost < 0:
        print("error: --enrollment > 0, --target-ratio > 0, --avg-teacher-cost >= 0", file=sys.stderr)
        return 2
    import math
    teachers_needed = a.enrollment / a.target_ratio
    salary_cost = teachers_needed * a.avg_teacher_cost
    print("=== Staffing ratio vs budget (CLAUDE.md S3 #3) ===")
    print(f"  Enrollment           : {a.enrollment:g}")
    print(f"  Target ratio         : {a.target_ratio:g}:1 (students per teacher)")
    print(f"  >> Teachers needed   : {teachers_needed:.1f} FTE  ({math.ceil(teachers_needed):g} rounded up)")
    print(f"  Avg teacher cost     : {_money(a.avg_teacher_cost)}")
    print(f"  >> Salary cost       : {_money(salary_cost)}")
    if a.current_teachers > 0:
        fte_var = teachers_needed - a.current_teachers
        cost_var = salary_cost - (a.current_teachers * a.avg_teacher_cost)
        direction = "MORE FTE / over current budget" if fte_var > 0 else "fewer FTE / under current budget"
        print(f"  Current FTE          : {a.current_teachers:g}")
        print(f"  >> Variance          : {fte_var:+.1f} FTE ({_money(cost_var)}) — {direction}")
        print("  NOTE: fit the ratio to the funded envelope, not an aspiration (S3 #3).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_absenteeism(a):
    if a.enrolled_students <= 0 or a.chronically_absent < 0:
        print("error: --enrolled-students > 0 and --chronically-absent >= 0", file=sys.stderr)
        return 2
    if a.chronically_absent > a.enrolled_students:
        print("error: --chronically-absent cannot exceed --enrolled-students", file=sys.stderr)
        return 2
    if not (0 < a.flag_threshold <= 1):
        print("error: 0 < --flag-threshold <= 1", file=sys.stderr)
        return 2
    chronic_rate = a.chronically_absent / a.enrolled_students
    print("=== Chronic absenteeism (CLAUDE.md S3 #5) ===")
    print(f"  Enrolled students    : {a.enrolled_students:g}")
    print(f"  Chronically absent   : {a.chronically_absent:g}")
    print(f"  >> Chronic-absence rate: {_pct(chronic_rate)}")
    print(f"  Flag threshold       : {_pct(a.flag_threshold)}  (source + date the definition, S3 #8)")
    if chronic_rate >= a.flag_threshold:
        print("  >> FLAG: chronic absenteeism at/over the early-warning threshold — intervene early, not at year-end (S3 #5)")
    else:
        print("  >> Below the flag threshold — monitor the trend, still an early signal (S3 #5)")
    if a.per_pupil_funding > 0:
        recovery = a.chronically_absent * a.per_pupil_funding * 0.05
        print(f"  >> Illustrative recovery upside: {_money(recovery)} (recovering ~5 ADA points across these students, S3 #2)")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='k12_school_administration_calc.py',
        description="K-12 School Administration decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('enrollment-funding', help='enrollment x per-pupil x ADA => funding + dollar value of each attendance point')
    sp.add_argument('--enrollment', type=float, required=True, help='enrolled students')
    sp.add_argument('--per-pupil-funding', type=float, required=True, help='per-pupil funding rate $')
    sp.add_argument('--ada-rate', type=float, default=1.0, help='average daily attendance rate (0-1)')
    sp.set_defaults(func=cmd_enrollment_funding)

    sp = sub.add_parser('staffing-ratio', help='enrollment / target ratio x avg cost => teachers, cost, variance')
    sp.add_argument('--enrollment', type=float, required=True, help='enrolled students')
    sp.add_argument('--target-ratio', type=float, required=True, help='target student:teacher ratio (students per teacher)')
    sp.add_argument('--avg-teacher-cost', type=float, required=True, help='average loaded teacher cost $')
    sp.add_argument('--current-teachers', type=float, default=0.0, help='current teaching FTE (for variance)')
    sp.set_defaults(func=cmd_staffing_ratio)

    sp = sub.add_parser('absenteeism', help='at/over-threshold / enrolled => chronic rate + flag + recovery upside')
    sp.add_argument('--enrolled-students', type=float, required=True, help='enrolled students')
    sp.add_argument('--chronically-absent', type=float, required=True, help='students at/over the chronic-absence threshold')
    sp.add_argument('--per-pupil-funding', type=float, default=0.0, help='per-pupil funding rate $ (for recovery upside)')
    sp.add_argument('--flag-threshold', type=float, default=0.1, help='chronic-absence rate that raises the flag (0-1)')
    sp.set_defaults(func=cmd_absenteeism)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
