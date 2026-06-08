#!/usr/bin/env python3
"""pharmacy_operations_calc.py — a zero-dependency Pharmacy Operations decision calculator.

Removes arithmetic error from 3 recurring pharmacy operations decisions:

  throughput-staffingTech + pharmacist hours to script volume plus clinical-service time.

  margin        Real per-script margin net of acquisition cost and DIR fee.

  adherence     PDC over the measurement period + adherence band + star implication.

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live
data. The user supplies every input; the tool does the arithmetic and shows the
formula. Stdlib only (argparse); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not professional/legal/regulatory/
financial advice (see ../CLAUDE.md S2). Validate every figure against the
client's actual data; route every professional determination to the qualified
authority. No patient PHI belongs in any input or output.
"""
from __future__ import annotations

import argparse
import sys

DISCLAIMER = (
    "Decision-support only — not professional/legal/regulatory/financial advice. "
    "Validate every input against the client's actual data; route professional "
    "determinations to the qualified authority (CLAUDE.md S2). No patient PHI."
)


def _pct(x):
    return f"{x * 100:.1f}%"


def _money(x):
    return f"${x:,.0f}"


def cmd_throughput_staffing(a):
    if a.scripts_per_tech_hour <= 0 or a.verifications_per_pharmacist_hour <= 0:
        print("error: per-hour rates must be > 0", file=sys.stderr)
        return 2
    tech_hours = a.daily_scripts / a.scripts_per_tech_hour
    verify_hours = a.daily_scripts / a.verifications_per_pharmacist_hour
    pharmacist_hours = verify_hours + a.clinical_service_hours
    print("=== Throughput staffing (CLAUDE.md S3 #1/#5) ===")
    print(f"  Daily scripts       : {a.daily_scripts:,.0f}")
    print(f"  >> Tech hours needed: {tech_hours:,.1f}  ({a.scripts_per_tech_hour:g}/h)")
    print(f"  Verification hours  : {verify_hours:,.1f}  ({a.verifications_per_pharmacist_hour:g}/h)")
    print(f"  Clinical-service hrs: {a.clinical_service_hours:g}")
    print(f"  >> Pharmacist hours needed: {pharmacist_hours:,.1f}  (verify + clinical)")
    if a.current_tech_hours > 0:
        tgap = tech_hours - a.current_tech_hours
        print(f"  Tech gap            : {tgap:+,.1f} h  (need - current)")
    if a.current_pharmacist_hours > 0:
        pgap = pharmacist_hours - a.current_pharmacist_hours
        print(f"  Pharmacist gap      : {pgap:+,.1f} h  (need - current)")
        if a.current_pharmacist_hours < verify_hours:
            print("  >> SAFETY: current pharmacist hours BELOW verification need — do NOT trade safety for speed (S3 #1)")
    print("  NOTE: verification capacity is a hard constraint; the clinical check is the pharmacist's (S3 #1 #8).")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_margin(a):
    if a.scripts <= 0:
        print("error: --scripts must be > 0", file=sys.stderr)
        return 2
    sticker = a.reimbursement - a.acquisition_cost
    real_margin = a.reimbursement - a.acquisition_cost - a.dir_fee
    total = real_margin * a.scripts
    print("=== Real margin net of DIR (CLAUDE.md S3 #3) ===")
    print(f"  Reimbursement/script: {_money(a.reimbursement)}")
    print(f"  Acquisition/script  : {_money(a.acquisition_cost)}")
    print(f"  Sticker margin      : {_money(sticker)} / script  (overstates — before DIR)")
    print(f"  DIR fee/script      : {_money(a.dir_fee)}")
    print(f"  >> Real margin      : {_money(real_margin)} / script")
    if a.scripts != 1:
        print(f"  Scripts             : {a.scripts:,.0f}")
        print(f"  >> Total real margin: {_money(total)}")
    if real_margin < 0:
        print("  >> WARNING: NEGATIVE margin after DIR — the sticker hid the loss (S3 #3); price specialty distinctly (S3 #6)")
    elif a.dir_fee > 0 and sticker > 0:
        erosion = (sticker - real_margin) / sticker if sticker else 0
        print(f"  >> DIR erodes {_pct(erosion)} of the sticker margin (S3 #3)")
    print(f"\n  {DISCLAIMER}")
    return 0

def cmd_adherence(a):
    if a.days_in_period <= 0:
        print("error: --days-in-period must be > 0", file=sys.stderr)
        return 2
    if not (0 < a.threshold <= 1):
        print("error: 0 < --threshold <= 1", file=sys.stderr)
        return 2
    pdc = a.days_covered / a.days_in_period
    print("=== Adherence: PDC + star implication (CLAUDE.md S3 #4) ===")
    print(f"  Days covered        : {a.days_covered:g}")
    print(f"  Days in period      : {a.days_in_period:g}")
    print(f"  >> PDC              : {_pct(pdc)}")
    print(f"  Band threshold      : {_pct(a.threshold)}")
    gap = a.threshold - pdc
    if pdc >= a.threshold:
        print(f"  >> ADHERENT — clears the band (surplus {_pct(pdc - a.threshold)}); supports the star measure (S3 #4)")
    else:
        extra_days = gap * a.days_in_period
        print(f"  >> BELOW band by {_pct(gap)} — drags the star measure and value-based reimbursement (S3 #4)")
        print(f"  >> ~{extra_days:,.1f} more covered days needed to clear the band — target near-threshold patients first")
    print("  NOTE: drug-therapy/clinical questions route to the licensed pharmacist (S3 #8).")
    print(f"\n  {DISCLAIMER}")
    return 0


def build_parser():
    p = argparse.ArgumentParser(
        prog='pharmacy_operations_calc.py',
        description="Pharmacy Operations decision calculator (stdlib only). Decision-support, not advice.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser('throughput-staffing', help='hours needed vs current, verification safety as the constraint')
    sp.add_argument('--daily-scripts', type=float, required=True, help='daily script volume')
    sp.add_argument('--scripts-per-tech-hour', type=float, required=True, help='scripts a tech processes per hour')
    sp.add_argument('--verifications-per-pharmacist-hour', type=float, required=True, help='scripts a pharmacist verifies per hour')
    sp.add_argument('--clinical-service-hours', type=float, default=0.0, help='daily pharmacist hours on clinical services')
    sp.add_argument('--current-tech-hours', type=float, default=0.0, help='current daily tech hours')
    sp.add_argument('--current-pharmacist-hours', type=float, default=0.0, help='current daily pharmacist hours')
    sp.set_defaults(func=cmd_throughput_staffing)

    sp = sub.add_parser('margin', help='reimbursement - acquisition - DIR; flag negative margin')
    sp.add_argument('--reimbursement', type=float, required=True, help='reimbursement per script $')
    sp.add_argument('--acquisition-cost', type=float, required=True, help='acquisition cost per script $')
    sp.add_argument('--dir-fee', type=float, default=0.0, help='DIR / clawback fee per script $')
    sp.add_argument('--scripts', type=float, default=1.0, help='script count (for total margin)')
    sp.set_defaults(func=cmd_margin)

    sp = sub.add_parser('adherence', help='PDC = days covered / days in period; band + star implication')
    sp.add_argument('--days-covered', type=float, required=True, help='days the patient had medication on hand')
    sp.add_argument('--days-in-period', type=float, required=True, help='days in the measurement period')
    sp.add_argument('--threshold', type=float, default=0.8, help='adherence band threshold for the star measure (0-1)')
    sp.set_defaults(func=cmd_adherence)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
