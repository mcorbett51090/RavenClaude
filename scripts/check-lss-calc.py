#!/usr/bin/env python3
"""Numeric-correctness gate for `plugins/process-improvement/scripts/lss_calc.py`.

lss_calc.py is the only executable in the process-improvement plugin, and every
number it prints goes straight into a tollgate deck: a capability index, a sigma
level, a control limit, a COPQ recovery figure. Until this file existed it had
ZERO coverage anywhere in the repo — no gate, no workflow, no test. A silent
arithmetic drift (a transposed control-chart constant, a `min` that became a
`max`, a dropped COPQ category) would have shipped green.

The battery below drives every advertised mode against inputs whose answers are
hand-checkable on paper, so a reviewer can audit the EXPECTATION, not just the
code:

  capability  USL 11 / LSL 9 / mu 10.2, sigma_w 0.30, sigma_o 0.42
              Cp  = 2 / (6 x 0.30) = 1.111
              Cpk = min(0.8/0.9, 1.2/0.9) = 0.889  -> below 1.0, NOT capable
              Pp  = 2 / (6 x 0.42) = 0.794
              Ppk = min(0.8/1.26, 1.2/1.26) = 0.635
              gap = 0.889 - 0.635 = +0.254 -> >0.2, drift called out
              Two more centred cases pin the band boundaries exactly:
              sigma 1.0 on a width-6 spec -> Cp = Cpk = 1.000 (marginal);
              sigma 0.5 on a width-6 spec -> Cp = Cpk = 2.000 (highly capable).

  sigma       The three textbook anchors of the 1.5-shift convention:
              3.4 DPMO -> 6.00 long / 4.50 short
              6,210    -> 4.00 long / 2.50 short
              66,807   -> 3.00 long / 1.50 short
              plus the raw-count path: 23 defects / (1500 units x 4 opps)
              = 23/6000 x 1e6 = 3,833.3 DPMO.

  imr         5,7,5,7,5,7 -> X-bar 6.0000, every MR = 2, so MR-bar 2.0000;
              I limits 6 +/- 2.66x2 = [0.6800, 11.3200]; MR UCL 3.267x2 =
              6.5340; no signal. Appending a 20 moves X-bar to 8.0000 and
              MR-bar to 23/6 = 3.8333, and BOTH charts must then signal at
              point #7 (20 > 18.1967, and its MR 13 > 12.5235).

  copq        120k + 80k + 40k = 240,000; /5,000,000 = 4.80%; 50% of the
              total = 120,000 recoverable.

`--self-test` is the teeth half: each mutant below must be CAUGHT and the
unmutated copy must stay CLEAN. A battery that flags everything is as useless as
one that flags nothing, so the clean control is asserted, not assumed.

Exit codes:  0 = clean;  2 = a finding (or broken teeth). Exit 1 is reserved for
a setup error, never for a finding.

Usage:
    python3 scripts/check-lss-calc.py               # live tree must be correct
    python3 scripts/check-lss-calc.py --self-test   # teeth: mutants caught
    python3 scripts/check-lss-calc.py --must-fail   # plant a wrong control-chart
                                                    # constant; MUST exit 2
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TARGET = Path("plugins/process-improvement/scripts/lss_calc.py")

# (case name, argv after the script path, substrings that MUST all appear)
# Every expectation is a value derivable by hand from the module docstring above.
CASES = [
    (
        "capability: off-centre, short vs long term",
        ["capability", "--usl", "11", "--lsl", "9", "--mean", "10.2",
         "--sigma-within", "0.30", "--sigma-overall", "0.42"],
        [
            "Cp  = 1.111",
            "Cpk = 0.889",
            "NOT capable",
            "Pp  = 0.794",
            "Ppk = 0.635",
            "Cpk - Ppk gap : +0.254",
            "large gap",
        ],
    ),
    (
        "capability: centred, Cp = Cpk = 1.000 (marginal band floor)",
        ["capability", "--usl", "10", "--lsl", "4", "--mean", "7",
         "--sigma-within", "1"],
        ["Cp  = 1.000", "Cpk = 1.000", "marginal"],
    ),
    (
        "capability: centred, Cp = Cpk = 2.000 (highly-capable band)",
        ["capability", "--usl", "13", "--lsl", "7", "--mean", "10",
         "--sigma-within", "0.5"],
        ["Cp  = 2.000", "Cpk = 2.000", "highly capable"],
    ),
    (
        "sigma: 3.4 DPMO is 6.00 long-term / 4.50 short-term",
        ["sigma", "--dpmo", "3.4"],
        [
            "DPMO  : 3.4",
            "yield : 99.99966%",
            "sigma (long-term, +1.5 shift) : 6.00",
            "sigma (short-term, no shift)  : 4.50",
        ],
    ),
    (
        "sigma: 6,210 DPMO is 4.00 long-term / 2.50 short-term",
        ["sigma", "--dpmo", "6210"],
        [
            "sigma (long-term, +1.5 shift) : 4.00",
            "sigma (short-term, no shift)  : 2.50",
        ],
    ),
    (
        "sigma: 66,807 DPMO is 3.00 long-term / 1.50 short-term",
        ["sigma", "--dpmo", "66807"],
        [
            "sigma (long-term, +1.5 shift) : 3.00",
            "sigma (short-term, no shift)  : 1.50",
        ],
    ),
    (
        "sigma: raw counts roll up to DPMO",
        ["sigma", "--defects", "23", "--units", "1500", "--opportunities", "4"],
        ["DPMO  : 3,833.3", "yield : 99.61667%"],
    ),
    (
        "imr: in-control series, limits and no signal",
        ["imr", "--values", "5,7,5,7,5,7"],
        [
            "X-bar (centerline): 6.0000",
            "MR-bar           : 2.0000",
            "UCL = 11.3200",
            "LCL = 0.6800",
            "UCL = 6.5340",
            "No point-beyond-limit signal",
        ],
    ),
    (
        "imr: one wild reading trips BOTH charts",
        ["imr", "--values", "5,7,5,7,5,7,20"],
        [
            "X-bar (centerline): 8.0000",
            "MR-bar           : 3.8333",
            "UCL = 18.1967",
            "LCL = -2.1967",
            "UCL = 12.5235",
            "OUT-OF-CONTROL (I chart)",
            "point #7 = 20",
            "OUT-OF-CONTROL (MR chart)",
            "MR at point #7 = 13",
        ],
    ),
    (
        "copq: three-category roll-up, % of revenue, recoverable",
        ["copq", "--internal", "120000", "--external", "80000",
         "--appraisal", "40000", "--revenue", "5000000",
         "--target-reduction", "50%"],
        [
            "-> COPQ total    : 240,000",
            "COPQ as % of revenue (5,000,000) : 4.80%",
            "at a 50% reduction target:",
            "recoverable COPQ : 120,000",
        ],
    ),
]

# (mutant name, literal to replace, replacement). Each must be caught by CASES.
# These are the failure modes that would actually ship: a transposed control-chart
# constant, an inverted Cpk, a silently re-based shift convention, a dropped COPQ
# category, a wrong capability denominator.
MUTANTS = [
    ("MR-chart D4 constant 3.267 -> 3.0", "_IMR_MR_UCL_FACTOR = 3.267",
     "_IMR_MR_UCL_FACTOR = 3.0"),
    ("I-chart 3/d2 constant 2.66 -> 3.0", "_IMR_I_FACTOR = 2.66",
     "_IMR_I_FACTOR = 3.0"),
    ("Cpk takes the WIDER side (min -> max)",
     "cpk = min((usl - mu) / (3.0 * sigma), (mu - lsl) / (3.0 * sigma))",
     "cpk = max((usl - mu) / (3.0 * sigma), (mu - lsl) / (3.0 * sigma))"),
    ("Cp denominator 6 sigma -> 3 sigma", "cp = (usl - lsl) / (6.0 * sigma)",
     "cp = (usl - lsl) / (3.0 * sigma)"),
    ("1.5-sigma shift silently re-based to 1.6", "{z + 1.5:.2f}", "{z + 1.6:.2f}"),
    ("COPQ drops the appraisal category",
     "copq = args.internal + args.external + args.appraisal",
     "copq = args.internal + args.external"),
]

# The --must-fail plant. A WRONG control-limit constant is the worst defect this
# tool can ship (it moves the line a plant reacts to), so it is the one used to
# prove the battery goes red on real arithmetic drift.
MUST_FAIL_MUTANT = MUTANTS[0]


def run_cases(target):
    """Drive every case against `target`; return one string per discrepancy."""
    failures = []
    for name, argv, expected in CASES:
        proc = subprocess.run(
            [sys.executable, str(target)] + argv,
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            failures.append(
                f"{name}: exited {proc.returncode} (stderr: {proc.stderr.strip()[:200]})"
            )
            continue
        for want in expected:
            if want not in proc.stdout:
                failures.append(f"{name}: expected {want!r} in the output, absent")
    return failures


def _mutate(src_text, needle, replacement):
    """Substitute once, refusing a no-op — a mutation that changes nothing is a
    fixture that silently stops testing (the shape this repo has been bitten by).
    """
    if needle not in src_text:
        raise LookupError(f"mutation anchor not found in lss_calc.py: {needle!r}")
    out = src_text.replace(needle, replacement, 1)
    if out == src_text:
        raise LookupError(f"mutation was a no-op: {needle!r}")
    return out


def _write_mutant(work, name, src_text, needle, replacement):
    path = work / (name.replace(" ", "-").replace("/", "-") + ".py")
    path.write_text(_mutate(src_text, needle, replacement), encoding="utf-8")
    return path


def run_real(target):
    failures = run_cases(target)
    if failures:
        print(f"check-lss-calc: {len(failures)} finding(s) in {target}", file=sys.stderr)
        for f in failures:
            print(f"  [wrong-value] {f}", file=sys.stderr)
        return 2
    print(f"check-lss-calc: {target} clean "
          f"({len(CASES)} cases across capability / sigma / imr / copq)")
    return 0


def run_must_fail(target):
    """Plant a wrong control-chart constant and let the battery judge it.

    Returns 2 when the battery correctly reddens; 1 when it does NOT (a setup
    failure loud enough to distinguish from a finding).
    """
    name, needle, replacement = MUST_FAIL_MUTANT
    src_text = target.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        try:
            mutant = _write_mutant(work, "must-fail", src_text, needle, replacement)
        except LookupError as exc:
            print(f"check-lss-calc: MUST-FAIL SETUP ERROR - {exc}", file=sys.stderr)
            return 1
        failures = run_cases(mutant)
    if not failures:
        print(f"check-lss-calc: TEETH BROKEN - planted mutant ({name}) was NOT caught",
              file=sys.stderr)
        return 1
    print(f"check-lss-calc: planted mutant ({name}) caught by "
          f"{len(failures)} assertion(s) - exiting 2 as designed", file=sys.stderr)
    for f in failures[:3]:
        print(f"  [wrong-value] {f}", file=sys.stderr)
    return 2


def self_test(target):
    ok = True
    src_text = target.read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)

        for name, needle, replacement in MUTANTS:
            try:
                mutant = _write_mutant(work, name, src_text, needle, replacement)
            except LookupError as exc:
                ok = False
                print(f"  x SETUP: {name} - {exc}")
                continue
            if run_cases(mutant):
                print(f"  + caught: {name}")
            else:
                ok = False
                print(f"  x MISSED: {name}")

        # Control: an unmutated COPY must be clean. Without this half a battery
        # that failed on everything (a bad path, a broken interpreter) would look
        # like perfect teeth.
        control = work / "control-lss_calc.py"
        shutil.copyfile(target, control)
        control_failures = run_cases(control)
        if control_failures:
            ok = False
            print("  x FLOODED: the unmutated copy is not clean (the red is the plant)")
            for f in control_failures:
                print(f"      {f}")
        else:
            print("  + clean:  the unmutated copy of lss_calc.py")

    print("\nteeth verified" if ok else "\nTEETH BROKEN")
    return 0 if ok else 2


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", default=str(TARGET))
    ap.add_argument("--self-test", action="store_true",
                    help="prove the battery's teeth: every mutant caught, control clean")
    ap.add_argument("--must-fail", action="store_true",
                    help="teeth: plant a wrong control-chart constant; MUST exit 2")
    args = ap.parse_args()

    target = Path(args.path)
    if not target.is_file():
        print(f"check-lss-calc: target not found: {target}", file=sys.stderr)
        return 1

    if args.self_test:
        return self_test(target)
    if args.must_fail:
        return run_must_fail(target)
    return run_real(target)


if __name__ == "__main__":
    sys.exit(main())
