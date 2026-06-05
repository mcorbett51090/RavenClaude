#!/usr/bin/env python3
"""lss_calc.py — a zero-dependency Lean Six Sigma decision calculator.

Removes arithmetic error from four recurring process-improvement computations a
Black Belt / process analyst runs constantly. It is a CALCULATOR, not a data
source — the user supplies every input; the tool does the arithmetic, shows the
formula, and states the verdict against the standard threshold.

  capability   Cp / Cpk / Pp / Ppk from spec limits + mean + a standard
               deviation. Cp/Cpk use the WITHIN-subgroup (short-term) sigma,
               Pp/Ppk the OVERALL (long-term) sigma — pass --sigma-within and/or
               --sigma-overall. Prints each index it can compute, bands it
               (<1.0 not capable / 1.0-1.33 marginal / >=1.33 capable /
               >=1.67 highly capable), and flags a large Cpk-vs-Ppk gap (drift).
               Pairs with knowledge/six-sigma-statistics-and-spc.md §2 and the
               capability-vs-control triage tree.

  sigma        Sigma level <-> DPMO <-> yield, with the explicit 1.5-sigma shift
               convention. Give --defects + --units + --opportunities (the tool
               computes DPMO) OR --dpmo directly; it prints DPMO, yield, and the
               long-term (shifted) AND short-term (unshifted) sigma level so the
               convention is never left ambiguous. Pairs with §1 of the same
               knowledge file and the "always state the shift convention"
               best-practice.

  imr          Individuals & Moving-Range (I-MR) control-chart limits from a
               series of individual readings. Prints the I-chart centerline +/-
               3-sigma limits (X-bar +/- 2.66*MR-bar) and the MR-chart limits
               (UCL = 3.267*MR-bar, LCL = 0), then scans the series against the
               point-outside-a-limit rule and reports any out-of-control points.
               CONTROL limits, not SPEC limits. Pairs with §3-4 and the
               control-chart-selection tree.

  copq        Cost of Poor Quality roll-up: sum internal-failure + external-
               failure + appraisal costs (prevention is excluded from the COPQ
               total by convention), express as a % of revenue, and project the
               recoverable amount at a target reduction. Pairs with the COPQ
               cost-category tree and the burning-platform best-practice.

Stdlib only (argparse + math); runs anywhere Python 3.8+ is present.

IMPORTANT: outputs are decision-support, not a substitute for the inferential
statistics seam. A capability CONFIDENCE INTERVAL, a Gage R&R %R&R, "is this
difference real?" (hypothesis test / DOE), and sample-size all route to the
applied-statistics plugin (see ../CLAUDE.md §8). This tool does the point
arithmetic and the threshold lookup; it does NOT certify statistical
significance, and capability on an OUT-OF-CONTROL process is meaningless — run
`imr` (or a control chart) and confirm stability BEFORE trusting `capability`.

Formulas (all verified 2026-06-05; full citations in
../knowledge/six-sigma-statistics-and-spc.md):
  Cp   = (USL - LSL) / (6 * sigma)
  Cpk  = min( (USL - mu)/(3*sigma), (mu - LSL)/(3*sigma) )
  Pp/Ppk identical to Cp/Cpk but using the OVERALL sigma.
  DPMO = defects / (units * opportunities) * 1_000_000
  yield = (1 - DPMO/1_000_000)
  sigma_long  = NORMSINV(1 - DPMO/1e6) + 1.5   (1.5-sigma-shift convention)
  sigma_short = NORMSINV(1 - DPMO/1e6)          (process potential, no shift)
  I-MR: I-chart UCL/LCL = X-bar +/- 2.66*MR-bar  (2.66 = 3/d2, d2=1.128 at n=2)
        MR-chart UCL = 3.267*MR-bar (D4 at n=2), LCL = 0

Examples
--------
  # Capability: spec 9.0-11.0, mean 10.2, short-term sigma 0.30, long-term 0.42
  python3 lss_calc.py capability --usl 11 --lsl 9 --mean 10.2 \\
      --sigma-within 0.30 --sigma-overall 0.42

  # Sigma level from raw counts: 23 defects over 1500 units, 4 opportunities each
  python3 lss_calc.py sigma --defects 23 --units 1500 --opportunities 4

  # Sigma level straight from a known DPMO
  python3 lss_calc.py sigma --dpmo 6210

  # I-MR limits + out-of-control scan over a reading series
  python3 lss_calc.py imr --values 10.1,10.3,9.8,10.0,12.4,10.2,9.9

  # COPQ roll-up: 120k internal + 80k external + 40k appraisal on 5M revenue,
  # projecting a 50% reduction
  python3 lss_calc.py copq --internal 120000 --external 80000 \\
      --appraisal 40000 --revenue 5000000 --target-reduction 50%
"""

from __future__ import annotations

import argparse
import math
import sys

# d2 = 1.128 and D4 = 3.267 are the control-chart constants for a moving range of
# n=2 (successive pairs); 2.66 = 3 / d2. Verified 2026-06-05 (JMP; Minitab; Six
# Sigma Study Guide) — see ../knowledge/six-sigma-statistics-and-spc.md §3.
_IMR_I_FACTOR = 2.66
_IMR_MR_UCL_FACTOR = 3.267


def _parse_rate(s: str) -> float:
    """Parse a rate like '50%' or '0.5' into a fraction (0.5)."""
    s = s.strip()
    try:
        return float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '50%' or '0.5', got {s!r}")


def _parse_values(s: str) -> list[float]:
    """Parse a comma- or whitespace-separated list of floats."""
    raw = s.replace(",", " ").split()
    if not raw:
        raise argparse.ArgumentTypeError("no values supplied")
    try:
        return [float(x) for x in raw]
    except ValueError:
        raise argparse.ArgumentTypeError(f"all values must be numbers, got {s!r}")


def _norm_inv(p: float) -> float:
    """Inverse standard-normal CDF (the NORMSINV used in the sigma conversion).

    Acklam's rational approximation; |error| < ~1.15e-9 over (0,1). Stdlib has no
    inverse-CDF, so we implement one rather than add a numpy/scipy dependency.
    """
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0, 1)")
    # Coefficients for Acklam's algorithm.
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    p_low, p_high = 0.02425, 1 - 0.02425
    if p < p_low:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p <= p_high:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
               (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)


def _capability_band(idx: float) -> str:
    """Band a Cpk/Ppk per the standard thresholds (knowledge file §2)."""
    if idx < 1.0:
        return "NOT capable (spread exceeds spec)"
    if idx < 1.33:
        return "marginal (capable only if centered + stable)"
    if idx < 1.67:
        return "capable (>=1.33 AIAG baseline, ~63 PPM)"
    return "highly capable (>=1.67 critical-characteristic grade)"


def _indices(usl: float, lsl: float, mu: float, sigma: float) -> tuple[float, float]:
    """Return (Cp-like, Cpk-like) for the given sigma. Caller labels short/long."""
    cp = (usl - lsl) / (6.0 * sigma)
    cpk = min((usl - mu) / (3.0 * sigma), (mu - lsl) / (3.0 * sigma))
    return cp, cpk


def cmd_capability(args: argparse.Namespace) -> int:
    if args.usl <= args.lsl:
        print("error: --usl must be greater than --lsl", file=sys.stderr)
        return 2
    if not (args.lsl <= args.mean <= args.usl):
        print("warning: --mean is OUTSIDE the spec limits — Cpk will be negative.",
              file=sys.stderr)
    if args.sigma_within is None and args.sigma_overall is None:
        print("error: supply --sigma-within and/or --sigma-overall", file=sys.stderr)
        return 2
    for name, val in (("--sigma-within", args.sigma_within),
                      ("--sigma-overall", args.sigma_overall)):
        if val is not None and val <= 0:
            print(f"error: {name} must be > 0", file=sys.stderr)
            return 2

    print("Process capability / performance")
    print(f"  spec limits   : LSL {args.lsl:g}  ..  USL {args.usl:g}  "
          f"(width {args.usl - args.lsl:g})")
    print(f"  process mean  : {args.mean:g}")

    cpk = ppk = None
    if args.sigma_within is not None:
        cp, cpk = _indices(args.usl, args.lsl, args.mean, args.sigma_within)
        print(f"  within sigma  : {args.sigma_within:g} (short-term)")
        print(f"    Cp  = {cp:.3f}   (potential, ignores centering)")
        print(f"    Cpk = {cpk:.3f}   -> {_capability_band(cpk)}")
    if args.sigma_overall is not None:
        pp, ppk = _indices(args.usl, args.lsl, args.mean, args.sigma_overall)
        print(f"  overall sigma : {args.sigma_overall:g} (long-term)")
        print(f"    Pp  = {pp:.3f}   (potential, ignores centering)")
        print(f"    Ppk = {ppk:.3f}   -> {_capability_band(ppk)}")

    if cpk is not None and ppk is not None:
        gap = cpk - ppk
        print()
        print(f"  Cpk - Ppk gap : {gap:+.3f}")
        if gap > 0.2:
            print("    -> large gap: short-term capability is NOT being held long-term")
            print("       (the process is drifting / unstable between subgroups).")
        else:
            print("    -> small gap: short- and long-term capability are consistent.")
    print()
    print("  NOTE: capability is meaningful ONLY on an in-CONTROL process. Confirm")
    print("        stability (run `imr` or a control chart) FIRST. A capability")
    print("        CONFIDENCE INTERVAL routes to applied-statistics (../CLAUDE.md §8).")
    return 0


def cmd_sigma(args: argparse.Namespace) -> int:
    if args.dpmo is not None:
        dpmo = args.dpmo
    else:
        if args.defects is None or args.units is None or args.opportunities is None:
            print("error: supply --dpmo OR all of --defects/--units/--opportunities",
                  file=sys.stderr)
            return 2
        if args.units <= 0 or args.opportunities <= 0:
            print("error: --units and --opportunities must be > 0", file=sys.stderr)
            return 2
        if args.defects < 0:
            print("error: --defects must be >= 0", file=sys.stderr)
            return 2
        dpmo = args.defects / (args.units * args.opportunities) * 1_000_000

    if not 0.0 <= dpmo < 1_000_000:
        print("error: DPMO must be in [0, 1,000,000)", file=sys.stderr)
        return 2

    yield_frac = 1.0 - dpmo / 1_000_000
    print("Sigma level <-> DPMO <-> yield")
    if args.dpmo is None:
        print(f"  defects / (units x opportunities) : {args.defects:g} / "
              f"({args.units:g} x {args.opportunities:g})")
    print(f"  DPMO  : {dpmo:,.1f}")
    print(f"  yield : {yield_frac * 100:.5f}%")

    if dpmo == 0.0:
        print("  sigma : zero defects in this sample — sigma is unbounded above.")
        print("          Collect more data; a finite sample can't prove 0 DPMO.")
        return 0

    p_good = 1.0 - dpmo / 1_000_000
    z = _norm_inv(p_good)
    print(f"  sigma (long-term, +1.5 shift) : {z + 1.5:.2f}")
    print(f"  sigma (short-term, no shift)  : {z:.2f}")
    print()
    print("  ALWAYS state which convention you quote. The famous '6 sigma = 3.4 DPMO'")
    print("  is the LONG-TERM (1.5-shift) number (../CLAUDE.md anti-pattern; §1).")
    return 0


def cmd_imr(args: argparse.Namespace) -> int:
    vals = args.values
    if len(vals) < 2:
        print("error: --values needs at least 2 readings", file=sys.stderr)
        return 2

    n = len(vals)
    xbar = sum(vals) / n
    moving_ranges = [abs(vals[i] - vals[i - 1]) for i in range(1, n)]
    mr_bar = sum(moving_ranges) / len(moving_ranges)

    i_ucl = xbar + _IMR_I_FACTOR * mr_bar
    i_lcl = xbar - _IMR_I_FACTOR * mr_bar
    mr_ucl = _IMR_MR_UCL_FACTOR * mr_bar

    print("I-MR control chart (Individuals & Moving Range)")
    print(f"  readings (n)     : {n}")
    print(f"  X-bar (centerline): {xbar:.4f}")
    print(f"  MR-bar           : {mr_bar:.4f}")
    print()
    print("  Individuals (I) chart  [centerline +/- 2.66 * MR-bar]:")
    print(f"    UCL = {i_ucl:.4f}")
    print(f"    CL  = {xbar:.4f}")
    print(f"    LCL = {i_lcl:.4f}")
    print("  Moving-Range (MR) chart:")
    print(f"    UCL = {mr_ucl:.4f}   (3.267 * MR-bar)")
    print(f"    CL  = {mr_bar:.4f}")
    print("    LCL = 0.0000   (a range can't be negative)")
    print()

    i_signals = [(i + 1, v) for i, v in enumerate(vals) if v > i_ucl or v < i_lcl]
    mr_signals = [(i + 2, mr) for i, mr in enumerate(moving_ranges) if mr > mr_ucl]
    if i_signals:
        print("  OUT-OF-CONTROL (I chart) — point beyond a 3-sigma limit:")
        for pos, v in i_signals:
            print(f"    point #{pos} = {v:g}  (outside [{i_lcl:.3f}, {i_ucl:.3f}])")
    if mr_signals:
        print("  OUT-OF-CONTROL (MR chart) — moving range beyond UCL:")
        for pos, mr in mr_signals:
            print(f"    MR at point #{pos} = {mr:g}  (> {mr_ucl:.3f})")
    if not i_signals and not mr_signals:
        print("  No point-beyond-limit signal. (This checks ONLY rule 1 — a full")
        print("  Western Electric / Nelson run-rule scan is a richer test; see §4.)")
    print()
    print("  These are CONTROL limits (voice of the process), NOT spec limits")
    print("  (voice of the customer). Stability != capability (../CLAUDE.md §4).")
    return 0


def cmd_copq(args: argparse.Namespace) -> int:
    for name, val in (("--internal", args.internal), ("--external", args.external),
                      ("--appraisal", args.appraisal)):
        if val < 0:
            print(f"error: {name} must be >= 0", file=sys.stderr)
            return 2
    if args.revenue is not None and args.revenue <= 0:
        print("error: --revenue must be > 0", file=sys.stderr)
        return 2

    copq = args.internal + args.external + args.appraisal
    print("Cost of Poor Quality (COPQ) roll-up")
    print(f"  internal failure : {args.internal:,.0f}  (rework, scrap, re-processing)")
    print(f"  external failure : {args.external:,.0f}  (returns, warranty, credits)")
    print(f"  appraisal        : {args.appraisal:,.0f}  (inspection, testing, audit)")
    print(f"  -> COPQ total    : {copq:,.0f}")
    print("     (prevention spend is EXCLUDED from COPQ by convention — it's the")
    print("      cure, not the failure; counting it double-charges the fix.)")

    if args.revenue is not None:
        pct = copq / args.revenue * 100.0
        print(f"  COPQ as % of revenue ({args.revenue:,.0f}) : {pct:.2f}%")
        print("    (a 15-20%-of-revenue COPQ is the classic 'hidden factory' figure;")
        print("     verify against the org's own cost data before quoting it.)")

    if args.target_reduction is not None:
        recoverable = copq * args.target_reduction
        print(f"  at a {args.target_reduction * 100:g}% reduction target:")
        print(f"    recoverable COPQ : {recoverable:,.0f}")
        print("    -> this is the burning-platform number for the project charter.")
    print()
    print("  NOTE: COPQ sizes the OPPORTUNITY; it does not prove a cause. Pair it")
    print("        with a proven root cause before committing the spend (§4 / #4).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lss_calc.py",
        description="Lean Six Sigma decision calculator (stdlib only). "
        "Decision-support, not statistical certification — the inference seam "
        "(CIs, Gage R&R, hypothesis tests, DOE) routes to applied-statistics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    cap = sub.add_parser("capability", help="Cp/Cpk/Pp/Ppk from spec + mean + sigma")
    cap.add_argument("--usl", type=float, required=True, help="upper spec limit")
    cap.add_argument("--lsl", type=float, required=True, help="lower spec limit")
    cap.add_argument("--mean", type=float, required=True, help="process mean (mu)")
    cap.add_argument("--sigma-within", type=float, default=None,
                     help="within-subgroup (short-term) std dev -> Cp/Cpk")
    cap.add_argument("--sigma-overall", type=float, default=None,
                     help="overall (long-term) std dev -> Pp/Ppk")
    cap.set_defaults(func=cmd_capability)

    sig = sub.add_parser("sigma", help="sigma level <-> DPMO <-> yield (1.5-shift stated)")
    sig.add_argument("--dpmo", type=float, default=None, help="DPMO directly")
    sig.add_argument("--defects", type=float, default=None, help="defect count")
    sig.add_argument("--units", type=float, default=None, help="units inspected")
    sig.add_argument("--opportunities", type=float, default=None,
                     help="defect opportunities per unit")
    sig.set_defaults(func=cmd_sigma)

    imr = sub.add_parser("imr", help="I-MR control-chart limits + out-of-control scan")
    imr.add_argument("--values", type=_parse_values, required=True,
                     help="comma/space-separated individual readings (>=2)")
    imr.set_defaults(func=cmd_imr)

    cop = sub.add_parser("copq", help="Cost of Poor Quality roll-up + recoverable")
    cop.add_argument("--internal", type=float, required=True,
                     help="internal-failure cost (rework, scrap)")
    cop.add_argument("--external", type=float, required=True,
                     help="external-failure cost (returns, warranty)")
    cop.add_argument("--appraisal", type=float, required=True,
                     help="appraisal cost (inspection, testing)")
    cop.add_argument("--revenue", type=float, default=None,
                     help="revenue to express COPQ as a % of (optional)")
    cop.add_argument("--target-reduction", type=_parse_rate, default=None,
                     help="reduction target for recoverable COPQ (e.g. 50%%)")
    cop.set_defaults(func=cmd_copq)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
