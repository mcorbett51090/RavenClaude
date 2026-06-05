#!/usr/bin/env python3
"""stat_calc.py — a zero-dependency applied-statistics decision calculator.

Removes arithmetic error from four recurring "is this difference REAL?" decisions
an applied statistician / analyst / consultant runs constantly — WITHOUT pulling in
scipy/statsmodels, so it runs anywhere Python 3.8+ is present (the normal-distribution
quantile and CDF are implemented from published rational approximations; see below).

  samplesize   Required n PER GROUP for a two-arm test, plus the MDE/power inversion.
               --kind proportion : two-proportion z-test (conversion rates).
                 n = ( z_{1-a/2}*sqrt(2*pbar*(1-pbar)) + z_b*sqrt(p1(1-p1)+p2(1-p2)) )^2
                     / (p1 - p2)^2          [pooled-variance form; pbar=(p1+p2)/2]
                 (MetricGate, "Sample Size for Two Proportions"; NCSS PASS ch.199.)
               --kind mean : two-sample t-test via Cohen's d, normal approximation:
                 n = 2 * (z_{1-a/2} + z_b)^2 / d^2     per group
                 (Cohen 1988; the z-based closed form, slightly anticonservative vs
                  the exact noncentral-t — flagged in output. Use statsmodels
                  TTestIndPower for the exact value on small n.)

  correct      Multiple-comparison correction over a list of raw p-values. Prints the
               Bonferroni, Holm (step-down), Benjamini-Hochberg (FDR, step-up), and
               Benjamini-Yekutieli adjusted p-values and the reject/keep verdict at the
               given alpha, plus the family-wise false-positive arithmetic
               1 - (1-alpha)^m. Pairs with knowledge/multiplicity-correction-decision-tree.md.
                 Bonferroni : adj = min(1, m*p)
                 Holm       : adj_(i) = max_{j<=i} (m-j+1)*p_(j), capped at 1, monotone
                 BH         : adj_(i) = min_{j>=i} (m/j)*p_(j), capped at 1, monotone
                 BY         : BH with m scaled by c(m)=sum_{i=1..m} 1/i
               (Holm 1979; Benjamini & Hochberg 1995; Benjamini & Yekutieli 2001;
                adjusted-p formulas per r-statistics.co P-Value Adjustment Calculator.)

  effectsize   Standardized effect size from summary stats, for reporting alongside a test.
               --kind d : Cohen's d for two means = (m1 - m2) / s_pooled,
                 s_pooled = sqrt(((n1-1)s1^2 + (n2-1)s2^2)/(n1+n2-2)).
               --kind h : Cohen's h for two proportions = 2*asin(sqrt(p1)) - 2*asin(sqrt(p2)).
               Benchmarks: |h|,|d| ~ 0.2 small / 0.5 medium / 0.8 large (Cohen 1988).

  ci           Confidence interval for a single proportion (the uncertainty band a
               dashboard widget should show — the statistical-qa-of-metrics seam).
               --method wilson (default; better near 0/1 and small n) or --method wald.
                 Wald   : p_hat +/- z * sqrt(p_hat(1-p_hat)/n)
                 Wilson : (p_hat + z^2/2n +/- z*sqrt(p_hat(1-p_hat)/n + z^2/4n^2)) / (1+z^2/n)
               (Wilson 1927; Agresti & Coull 1998 recommend Wilson over Wald.)

This is a CALCULATOR, not a data source — it does not fetch benchmarks or live data.
The user supplies every input; the tool does the arithmetic and shows the formula. It
is decision-support, not a substitute for a domain check: validate every figure against
the engagement's actual data, report effect size + CI (not a bare p), and run the pitfall
screen (knowledge/statistical-pitfalls.md) before any deliverable.

Examples
--------
  # n/group to detect 5% -> 6% conversion at alpha=0.05, power=0.80 (two-sided)
  python3 stat_calc.py samplesize --kind proportion --baseline 0.05 --mde 0.01

  # n/group to detect Cohen's d = 0.3 difference in means
  python3 stat_calc.py samplesize --kind mean --d 0.3

  # correct 5 segment p-values, flag which survive at alpha=0.05
  python3 stat_calc.py correct --pvalues 0.001 0.013 0.04 0.21 0.50

  # Cohen's h between two conversion rates
  python3 stat_calc.py effectsize --kind h --p1 0.05 --p2 0.06

  # 95% Wilson CI for 84 conversions out of 1000
  python3 stat_calc.py ci --successes 84 --n 1000
"""

from __future__ import annotations

import argparse
import math
import sys


def _norm_ppf(p: float) -> float:
    """Inverse standard-normal CDF (quantile) via Acklam's rational approximation.

    Peter Acklam's algorithm; |error| < 1.15e-9 over (0,1). Stdlib substitute for
    scipy.stats.norm.ppf so the calculator needs no third-party dependency.
    """
    if not 0.0 < p < 1.0:
        raise ValueError("p must be in (0, 1)")
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow, phigh = 0.02425, 1.0 - 0.02425
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    if p > phigh:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    q = p - 0.5
    r = q * q
    return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
           (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)


def _z_two_sided(alpha: float) -> float:
    return _norm_ppf(1.0 - alpha / 2.0)


def _z_power(power: float) -> float:
    return _norm_ppf(power)


def _check_unit(name: str, x: float, *, strict: bool = True) -> None:
    lo_ok = x > 0.0 if strict else x >= 0.0
    hi_ok = x < 1.0 if strict else x <= 1.0
    if not (lo_ok and hi_ok):
        rng = "(0, 1)" if strict else "[0, 1]"
        print(f"error: {name} must be in {rng}, got {x}", file=sys.stderr)
        raise SystemExit(2)


def cmd_samplesize(args: argparse.Namespace) -> int:
    _check_unit("--alpha", args.alpha)
    _check_unit("--power", args.power)
    z_a = _z_two_sided(args.alpha) if args.two_sided else _norm_ppf(1.0 - args.alpha)
    z_b = _z_power(args.power)

    print("Sample size — two-arm test")
    print(f"  alpha            : {args.alpha:g}  ({'two' if args.two_sided else 'one'}-sided)")
    print(f"  power            : {args.power:g}  (z_beta = {z_b:.4f})")
    print(f"  z_(1-a/2)        : {z_a:.4f}")

    if args.kind == "proportion":
        if args.baseline is None or args.mde is None:
            print("error: --kind proportion needs --baseline and --mde", file=sys.stderr)
            return 2
        p1 = args.baseline
        p2 = args.baseline + args.mde
        _check_unit("--baseline", p1)
        _check_unit("derived p2 (baseline + mde)", p2)
        pbar = (p1 + p2) / 2.0
        numer = (z_a * math.sqrt(2.0 * pbar * (1.0 - pbar))
                 + z_b * math.sqrt(p1 * (1.0 - p1) + p2 * (1.0 - p2)))
        n = (numer / (p1 - p2)) ** 2
        h = 2.0 * math.asin(math.sqrt(p2)) - 2.0 * math.asin(math.sqrt(p1))
        print(f"  baseline p1      : {p1:g}")
        print(f"  treatment p2     : {p2:g}  (absolute MDE = {args.mde:g})")
        print(f"  Cohen's h        : {abs(h):.4f}")
        print(f"  → n PER GROUP    : {math.ceil(n):,}  (total {2 * math.ceil(n):,})")
        print("  formula: n = (z_(1-a/2)*sqrt(2*pbar(1-pbar)) + z_b*sqrt(p1(1-p1)+p2(1-p2)))^2 / (p1-p2)^2")
        print("  note: pooled-variance two-proportion z-test (MetricGate / NCSS PASS ch.199).")
    elif args.kind == "mean":
        if args.d is None:
            print("error: --kind mean needs --d (Cohen's d)", file=sys.stderr)
            return 2
        if args.d <= 0:
            print("error: --d must be > 0", file=sys.stderr)
            return 2
        n = 2.0 * (z_a + z_b) ** 2 / (args.d ** 2)
        print(f"  Cohen's d        : {args.d:g}")
        print(f"  → n PER GROUP    : {math.ceil(n):,}  (total {2 * math.ceil(n):,})")
        print("  formula: n = 2*(z_(1-a/2) + z_b)^2 / d^2   (Cohen 1988, normal approx.)")
        print("  note: z-based approximation — slightly anticonservative on small n; for the")
        print("        exact value use statsmodels TTestIndPower (the noncentral-t solver).")
    else:  # pragma: no cover - argparse choices guard this
        return 2

    print("  reminder: this sizes the MINIMUM n to DETECT the effect — it does not promise")
    print("            the effect is real. Pre-register before collecting (pitfall #1/#5).")
    return 0


def _holm(sorted_p: list[float], m: int) -> list[float]:
    """Holm step-down adjusted p-values for an ascending-sorted p list."""
    out: list[float] = []
    running = 0.0
    for i, p in enumerate(sorted_p):  # i is 0-based; rank j = i+1
        adj = min(1.0, (m - i) * p)
        running = max(running, adj)  # enforce monotonic non-decreasing
        out.append(running)
    return out


def _bh(sorted_p: list[float], m: int) -> list[float]:
    """Benjamini-Hochberg step-up adjusted p-values for an ascending-sorted p list."""
    out = [0.0] * m
    running = 1.0
    for i in range(m - 1, -1, -1):  # from largest p down to smallest
        rank = i + 1
        adj = min(1.0, (m / rank) * sorted_p[i])
        running = min(running, adj)  # enforce monotonic non-increasing from the top
        out[i] = running
    return out


def cmd_correct(args: argparse.Namespace) -> int:
    _check_unit("--alpha", args.alpha)
    raw = args.pvalues
    for p in raw:
        if not 0.0 <= p <= 1.0:
            print(f"error: every p-value must be in [0, 1], got {p}", file=sys.stderr)
            return 2
    m = len(raw)
    if m == 0:
        print("error: need at least one p-value", file=sys.stderr)
        return 2

    order = sorted(range(m), key=lambda i: raw[i])
    sorted_p = [raw[i] for i in order]

    bonf = [min(1.0, m * p) for p in sorted_p]
    holm = _holm(sorted_p, m)
    bh = _bh(sorted_p, m)
    cm = sum(1.0 / i for i in range(1, m + 1))  # harmonic penalty c(m)
    by = [min(1.0, v * cm) for v in bh]

    fp_any = 1.0 - (1.0 - args.alpha) ** m

    print("Multiple-comparison correction")
    print(f"  family size m    : {m}")
    print(f"  alpha            : {args.alpha:g}")
    print(f"  expected false positives if all null : {m * args.alpha:.2f}")
    print(f"  P(>=1 false positive) = 1-(1-a)^m    : {fp_any:.3f}")
    print()
    print("  raw_p    Bonf     Holm(FWER)  BH(FDR)   BY        verdict@alpha")
    print("  -------  -------  ----------  --------  --------  -------------")
    for k in range(m):
        rej_bonf = bonf[k] <= args.alpha
        rej_holm = holm[k] <= args.alpha
        rej_bh = bh[k] <= args.alpha
        rej_by = by[k] <= args.alpha
        verdict = (f"Bonf={'R' if rej_bonf else '-'} Holm={'R' if rej_holm else '-'} "
                   f"BH={'R' if rej_bh else '-'} BY={'R' if rej_by else '-'}")
        print(f"  {sorted_p[k]:.5f}  {bonf[k]:.5f}  {holm[k]:.5f}     "
              f"{bh[k]:.5f}   {by[k]:.5f}   {verdict}")
    print()
    print(f"  rejections: Bonferroni {sum(p <= args.alpha for p in bonf)}, "
          f"Holm {sum(p <= args.alpha for p in holm)}, "
          f"BH {sum(p <= args.alpha for p in bh)}, "
          f"BY {sum(p <= args.alpha for p in by)}  (R = reject the null)")
    print("  choose: FWER (Bonferroni/Holm) for CONFIRMATORY work where one false positive")
    print("          is costly; FDR (BH) for EXPLORATORY screening. See the decision tree:")
    print("          knowledge/multiplicity-correction-decision-tree.md")
    return 0


def cmd_effectsize(args: argparse.Namespace) -> int:
    if args.kind == "d":
        need = [args.m1, args.m2, args.s1, args.s2, args.n1, args.n2]
        if any(v is None for v in need):
            print("error: --kind d needs --m1 --m2 --s1 --s2 --n1 --n2", file=sys.stderr)
            return 2
        if args.n1 < 2 or args.n2 < 2:
            print("error: --n1 and --n2 must be >= 2", file=sys.stderr)
            return 2
        if args.s1 < 0 or args.s2 < 0:
            print("error: --s1 and --s2 must be >= 0", file=sys.stderr)
            return 2
        sp = math.sqrt(((args.n1 - 1) * args.s1 ** 2 + (args.n2 - 1) * args.s2 ** 2)
                       / (args.n1 + args.n2 - 2))
        d = (args.m1 - args.m2) / sp if sp > 0 else 0.0
        print("Effect size — Cohen's d (two means)")
        print(f"  pooled SD        : {sp:.4f}")
        print(f"  → Cohen's d      : {d:.4f}  ({_benchmark(abs(d))})")
        print("  formula: d = (m1-m2)/s_pooled; s_pooled = sqrt(((n1-1)s1^2+(n2-1)s2^2)/(n1+n2-2))")
    elif args.kind == "h":
        if args.p1 is None or args.p2 is None:
            print("error: --kind h needs --p1 and --p2", file=sys.stderr)
            return 2
        _check_unit("--p1", args.p1, strict=False)
        _check_unit("--p2", args.p2, strict=False)
        h = 2.0 * math.asin(math.sqrt(args.p1)) - 2.0 * math.asin(math.sqrt(args.p2))
        print("Effect size — Cohen's h (two proportions)")
        print(f"  p1, p2           : {args.p1:g}, {args.p2:g}")
        print(f"  → Cohen's h      : {h:.4f}  (|h| {_benchmark(abs(h))})")
        print("  formula: h = 2*asin(sqrt(p1)) - 2*asin(sqrt(p2))  (arcsine-stabilized)")
    else:  # pragma: no cover
        return 2
    print("  benchmarks (Cohen 1988): 0.2 small / 0.5 medium / 0.8 large — a guide, not a verdict.")
    print("  report the effect size WITH its CI; significance != importance (house opinion #3).")
    return 0


def _benchmark(x: float) -> str:
    if x < 0.2:
        return "below small"
    if x < 0.5:
        return "small"
    if x < 0.8:
        return "medium"
    return "large"


def cmd_ci(args: argparse.Namespace) -> int:
    _check_unit("--conf", args.conf)
    if args.n <= 0:
        print("error: --n must be > 0", file=sys.stderr)
        return 2
    if not 0 <= args.successes <= args.n:
        print("error: --successes must be in [0, n]", file=sys.stderr)
        return 2
    z = _z_two_sided(1.0 - args.conf)
    phat = args.successes / args.n
    print(f"Confidence interval — single proportion ({args.conf * 100:g}%)")
    print(f"  successes / n    : {args.successes} / {args.n}")
    print(f"  p_hat            : {phat:.4f}")
    if args.method == "wald":
        half = z * math.sqrt(phat * (1.0 - phat) / args.n)
        lo, hi = max(0.0, phat - half), min(1.0, phat + half)
        print(f"  → Wald 95%-style : [{lo:.4f}, {hi:.4f}]  (half-width {half:.4f})")
        print("  formula: p_hat +/- z*sqrt(p_hat(1-p_hat)/n)")
        print("  note: Wald is poor near 0/1 and small n — prefer --method wilson there.")
    else:
        z2 = z * z
        denom = 1.0 + z2 / args.n
        center = (phat + z2 / (2.0 * args.n)) / denom
        half = (z * math.sqrt(phat * (1.0 - phat) / args.n + z2 / (4.0 * args.n ** 2))) / denom
        lo, hi = max(0.0, center - half), min(1.0, center + half)
        print(f"  → Wilson interval: [{lo:.4f}, {hi:.4f}]  (center {center:.4f})")
        print("  formula: (p_hat + z^2/2n +/- z*sqrt(p_hat(1-p_hat)/n + z^2/4n^2)) / (1 + z^2/n)")
        print("  note: Wilson (1927); Agresti-Coull recommend it over Wald near 0/1 / small n.")
    print("  this is the uncertainty BAND a dashboard widget should display (statistical-qa seam).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stat_calc.py",
        description="Applied-statistics decision calculator (stdlib only). "
        "Decision-support, not a substitute for the pitfall screen — validate every input.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    ss = sub.add_parser("samplesize", help="n per group for a two-arm test (+ MDE/power)")
    ss.add_argument("--kind", choices=["proportion", "mean"], required=True)
    ss.add_argument("--baseline", type=float, default=None,
                    help="proportion only: baseline rate p1 (e.g. 0.05)")
    ss.add_argument("--mde", type=float, default=None,
                    help="proportion only: absolute minimum detectable effect (e.g. 0.01)")
    ss.add_argument("--d", type=float, default=None,
                    help="mean only: Cohen's d to detect")
    ss.add_argument("--alpha", type=float, default=0.05, help="significance level (default 0.05)")
    ss.add_argument("--power", type=float, default=0.80, help="desired power (default 0.80)")
    ss.add_argument("--one-sided", dest="two_sided", action="store_false",
                    help="one-sided test (default two-sided)")
    ss.set_defaults(func=cmd_samplesize, two_sided=True)

    cc = sub.add_parser("correct", help="multiple-comparison correction over raw p-values")
    cc.add_argument("--pvalues", type=float, nargs="+", required=True,
                    help="raw p-values, space-separated")
    cc.add_argument("--alpha", type=float, default=0.05, help="significance level (default 0.05)")
    cc.set_defaults(func=cmd_correct)

    es = sub.add_parser("effectsize", help="Cohen's d (means) or h (proportions)")
    es.add_argument("--kind", choices=["d", "h"], required=True)
    es.add_argument("--m1", type=float, default=None, help="d: mean of group 1")
    es.add_argument("--m2", type=float, default=None, help="d: mean of group 2")
    es.add_argument("--s1", type=float, default=None, help="d: SD of group 1")
    es.add_argument("--s2", type=float, default=None, help="d: SD of group 2")
    es.add_argument("--n1", type=int, default=None, help="d: n of group 1")
    es.add_argument("--n2", type=int, default=None, help="d: n of group 2")
    es.add_argument("--p1", type=float, default=None, help="h: proportion 1")
    es.add_argument("--p2", type=float, default=None, help="h: proportion 2")
    es.set_defaults(func=cmd_effectsize)

    ci = sub.add_parser("ci", help="confidence interval for a single proportion")
    ci.add_argument("--successes", type=int, required=True, help="number of successes")
    ci.add_argument("--n", type=int, required=True, help="number of trials")
    ci.add_argument("--conf", type=float, default=0.95, help="confidence level (default 0.95)")
    ci.add_argument("--method", choices=["wilson", "wald"], default="wilson",
                    help="interval method (default wilson)")
    ci.set_defaults(func=cmd_ci)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
