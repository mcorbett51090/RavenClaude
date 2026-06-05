#!/usr/bin/env python3
"""experiment_calc.py — a zero-dependency A/B-test design calculator.

Removes arithmetic error from the three numbers an experimentation engineer
sizes constantly BEFORE a test runs, plus the one integrity check that decides
whether a finished test can be read at all:

  sample-size   Per-arm sample size for a two-proportion test, given a baseline
                conversion rate, the minimum detectable effect (MDE), alpha, and
                power. Uses the standard normal-approximation two-proportion
                formula. Prints the per-arm and total N, and (optionally) the
                test duration given daily eligible traffic.

  mde           The inverse: the smallest effect a FIXED sample can detect at the
                given alpha/power. Answers "we only have N users/week and two
                weeks — what lift can we even see?" — the underpowered-test check.

  power         The achieved power of a test that already ran (or is planned) at a
                given per-arm N, baseline, and effect. Answers "was that flat
                result a true null, or were we underpowered?"

  srm           Sample-Ratio-Mismatch check: a chi-square goodness-of-fit test of
                observed arm counts against the intended split. A small p-value
                means assignment is broken and the result is INVALID regardless of
                significance. Default alarm threshold p < 0.001 (industry norm).

This is a CALCULATOR, not a data source — it fetches nothing; the user supplies
every input and the tool shows the formula. Stdlib only (argparse + math); runs
anywhere Python 3.8+ is present.

DESIGN-TIME ONLY. This tool sizes the apparatus (N, MDE, power) and runs the SRM
*trustworthiness* gate. It deliberately does NOT compute a significance verdict /
confidence interval / p-value on your PRIMARY metric — rigorous inferential
statistics (sequential boundaries, CUPED, multiple-comparison correction, the
"is the lift real" call) belong to the `applied-statistics` plugin. Route the
clean assignment + exposure + metric data there for the verdict (CLAUDE.md §3 #1).

The normal-approximation z-quantiles below use a rational approximation
(Acklam/Beasley-Springer-Moro shape) accurate to ~1e-9 over the usable range, so
the script stays stdlib-only (no scipy). Validate the design against your real
traffic before committing a test horizon.

Formulas (cited; see ../knowledge and the sources in CHANGELOG.md)
------------------------------------------------------------------
  Two-proportion per-arm sample size (normal approximation):
      n = ( z_{1-alpha/2}*sqrt(2*p_bar*(1-p_bar))
            + z_{1-beta}*sqrt(p1*(1-p1)+p2*(1-p2)) )^2 / (p2-p1)^2
    where p1 = baseline, p2 = p1 + MDE (absolute), p_bar = (p1+p2)/2.
    Source: Two-proportion Z-test, en.wikipedia.org/wiki/Two-proportion_Z-test;
    derivation: towardsdatascience.com "Probing into Minimum Sample Size Formula".

  SRM chi-square goodness-of-fit (k arms, k-1 dof):
      X^2 = sum_i (observed_i - expected_i)^2 / expected_i
    For 2 arms (1 dof) X^2 > 10.83  <=>  p < 0.001.
    Source: convert.com SRM guide; docs.geteppo.com/statistics/sample-ratio-mismatch.

Examples
--------
  # Size a test: 5% baseline conversion, want to detect a +0.5pp absolute lift
  # (5.0% -> 5.5%), alpha 0.05 two-sided, 80% power, 20000 eligible users/day
  python3 experiment_calc.py sample-size --baseline 5% --mde 0.5pp \\
      --alpha 0.05 --power 80% --daily-traffic 20000

  # Detect a RELATIVE lift instead (a 10% relative lift on a 5% base = +0.5pp)
  python3 experiment_calc.py sample-size --baseline 5% --mde 10% --relative

  # Smallest detectable effect from a fixed sample of 50k per arm
  python3 experiment_calc.py mde --baseline 5% --per-arm 50000 --power 80%

  # Achieved power of a test that ran at 30k/arm for a +0.4pp effect
  python3 experiment_calc.py power --baseline 5% --mde 0.4pp --per-arm 30000

  # SRM check: intended 50/50, observed 10243 vs 9684
  python3 experiment_calc.py srm --observed 10243 9684 --split 50 50
"""

from __future__ import annotations

import argparse
import math
import sys


def _parse_rate(s: str) -> float:
    """Parse '5%' or '0.05' into a fraction (0.05). Rejects out-of-[0,1]."""
    s = s.strip()
    try:
        v = float(s[:-1]) / 100.0 if s.endswith("%") else float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be like '5%' or '0.05', got {s!r}")
    if not 0.0 < v < 1.0:
        raise argparse.ArgumentTypeError(f"rate must be in (0, 1), got {v}")
    return v


def _parse_effect(s: str) -> tuple[float, str]:
    """Parse an effect size. Returns (value, unit) where unit is 'pp' (absolute
    percentage points), 'pct' (relative percent), or 'abs' (bare fraction)."""
    s = s.strip().lower()
    try:
        if s.endswith("pp"):
            return float(s[:-2]) / 100.0, "pp"
        if s.endswith("%"):
            return float(s[:-1]) / 100.0, "pct"
        return float(s), "abs"
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"effect must be like '0.5pp', '10%', or '0.005', got {s!r}"
        )


def _z_quantile(p: float) -> float:
    """Inverse standard-normal CDF (probit) via the Acklam rational approximation.

    Accurate to ~1.15e-9 absolute over (0,1). Stdlib-only substitute for
    scipy.stats.norm.ppf so this script needs no third-party dependency.
    Reference: P.J. Acklam, "An algorithm for computing the inverse normal
    cumulative distribution function".
    """
    if not 0.0 < p < 1.0:
        raise ValueError("z-quantile probability must be in (0, 1)")
    a = [-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    p_low, p_high = 0.02425, 1.0 - 0.02425
    if p < p_low:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    if p <= p_high:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
               (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
    q = math.sqrt(-2.0 * math.log(1.0 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
           ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)


def _normal_cdf(z: float) -> float:
    """Standard-normal CDF via the error function (stdlib math.erf)."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _treatment_rate(baseline: float, effect: float, unit: str) -> float:
    """Resolve the treatment proportion p2 from baseline + an effect spec."""
    if unit == "pct":  # relative percent lift
        p2 = baseline * (1.0 + effect)
    else:  # 'pp' absolute (already /100) or 'abs' bare fraction
        p2 = baseline + effect
    if not 0.0 < p2 < 1.0:
        raise SystemExit(
            f"error: implied treatment rate {p2:.4%} is outside (0%, 100%) — "
            "check the baseline/MDE combination"
        )
    return p2


def _per_arm_n(p1: float, p2: float, alpha: float, power: float) -> float:
    """Two-proportion normal-approximation per-arm sample size (two-sided)."""
    z_alpha = _z_quantile(1.0 - alpha / 2.0)
    z_beta = _z_quantile(power)
    p_bar = (p1 + p2) / 2.0
    numerator = (
        z_alpha * math.sqrt(2.0 * p_bar * (1.0 - p_bar))
        + z_beta * math.sqrt(p1 * (1.0 - p1) + p2 * (1.0 - p2))
    ) ** 2
    return numerator / (p2 - p1) ** 2


def cmd_sample_size(args: argparse.Namespace) -> int:
    p1 = args.baseline
    effect, unit = args.mde
    if args.relative and unit == "pp":
        print("error: --relative conflicts with a 'pp' (absolute) --mde unit", file=sys.stderr)
        return 2
    if args.relative and unit == "abs":
        unit = "pct"  # bare number under --relative means a relative fraction
    p2 = _treatment_rate(p1, effect, unit)

    n = _per_arm_n(p1, p2, args.alpha, args.power)
    n_ceil = math.ceil(n)

    print("Two-proportion sample size (normal approximation, two-sided)")
    print(f"  baseline rate p1     : {p1:.4%}")
    print(f"  treatment rate p2    : {p2:.4%}  (MDE = {p2 - p1:+.4%} absolute, "
          f"{(p2 - p1) / p1:+.2%} relative)")
    print(f"  alpha (two-sided)    : {args.alpha:g}")
    print(f"  power (1 - beta)     : {args.power:.0%}")
    print(f"  → per-arm N          : {n_ceil:,}")
    print(f"  → total N (2 arms)   : {2 * n_ceil:,}")

    if args.daily_traffic is not None:
        if args.daily_traffic <= 0:
            print("error: --daily-traffic must be > 0", file=sys.stderr)
            return 2
        days = (2 * n_ceil) / args.daily_traffic
        print(f"  at {args.daily_traffic:,.0f} eligible users/day across both arms:")
        print(f"  → est. duration      : {days:.1f} days ({days / 7.0:.1f} weeks)")
        print("    reminder: run full business-cycle weeks, not just to N, to absorb")
        print("    weekday/weekend + novelty effects (no peeking — pre-register the horizon).")
    print("  note: significance / the 'is the lift real' verdict is applied-statistics'.")
    return 0


def cmd_mde(args: argparse.Namespace) -> int:
    """Smallest absolute effect detectable at a fixed per-arm N (bisection)."""
    p1 = args.baseline
    if args.per_arm < 2:
        print("error: --per-arm must be >= 2", file=sys.stderr)
        return 2
    target_n = float(args.per_arm)

    # Bisection on the absolute effect delta in (0, max_delta).
    max_delta = min(1.0 - p1, p1) - 1e-6  # keep p2 strictly inside (0,1)
    lo, hi = 1e-9, max_delta
    if _per_arm_n(p1, p1 + hi, args.alpha, args.power) > target_n:
        print("Minimum detectable effect at fixed sample")
        print(f"  baseline rate p1 : {p1:.4%}")
        print(f"  per-arm N        : {args.per_arm:,}")
        print(f"  → even the largest sane effect needs more than {args.per_arm:,}/arm at "
              f"{args.power:.0%} power — this sample is underpowered for any realistic lift.")
        return 0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _per_arm_n(p1, p1 + mid, args.alpha, args.power) > target_n:
            lo = mid
        else:
            hi = mid
    delta = hi
    p2 = p1 + delta
    print("Minimum detectable effect at fixed sample (two-sided)")
    print(f"  baseline rate p1     : {p1:.4%}")
    print(f"  per-arm N            : {args.per_arm:,}")
    print(f"  alpha (two-sided)    : {args.alpha:g}")
    print(f"  power (1 - beta)     : {args.power:.0%}")
    print(f"  → smallest MDE       : {delta:+.4%} absolute  ({delta / p1:+.2%} relative)")
    print(f"    (detectable treatment rate >= {p2:.4%})")
    print("  note: an effect smaller than this will read 'flat' even if real — that's")
    print("        an underpowered test, NOT evidence of no effect (route to applied-statistics).")
    return 0


def cmd_power(args: argparse.Namespace) -> int:
    """Achieved power for a given per-arm N, baseline, and effect."""
    p1 = args.baseline
    effect, unit = args.mde
    if args.relative and unit == "abs":
        unit = "pct"
    p2 = _treatment_rate(p1, effect, unit)
    if args.per_arm < 2:
        print("error: --per-arm must be >= 2", file=sys.stderr)
        return 2
    n = float(args.per_arm)

    z_alpha = _z_quantile(1.0 - args.alpha / 2.0)
    p_bar = (p1 + p2) / 2.0
    se_null = math.sqrt(2.0 * p_bar * (1.0 - p_bar) / n)
    se_alt = math.sqrt((p1 * (1.0 - p1) + p2 * (1.0 - p2)) / n)
    # Power = P(reject H0 | H1). z_beta = (|p2-p1| - z_alpha*se_null) / se_alt
    z_beta = (abs(p2 - p1) - z_alpha * se_null) / se_alt
    power = _normal_cdf(z_beta)

    print("Achieved statistical power (two-proportion, two-sided)")
    print(f"  baseline rate p1     : {p1:.4%}")
    print(f"  treatment rate p2    : {p2:.4%}  (effect {p2 - p1:+.4%} absolute)")
    print(f"  per-arm N            : {args.per_arm:,}")
    print(f"  alpha (two-sided)    : {args.alpha:g}")
    print(f"  → achieved power     : {power:.1%}")
    if power < 0.8:
        print("    UNDERPOWERED (< 80%): a true effect of this size will often read flat.")
        print("    A null result here is inconclusive, not 'no effect'.")
    else:
        print("    adequately powered (>= 80%) for an effect of this size.")
    print("  note: power is a design property; the significance call is applied-statistics'.")
    return 0


def cmd_srm(args: argparse.Namespace) -> int:
    """Chi-square goodness-of-fit SRM check (k arms, k-1 dof)."""
    observed = [float(x) for x in args.observed]
    if any(o < 0 for o in observed):
        print("error: observed counts must be >= 0", file=sys.stderr)
        return 2
    k = len(observed)
    if k < 2:
        print("error: --observed needs >= 2 arm counts", file=sys.stderr)
        return 2

    if args.split is not None:
        if len(args.split) != k:
            print(f"error: --split needs {k} weights to match {k} observed arms", file=sys.stderr)
            return 2
        weights = [float(w) for w in args.split]
    else:
        weights = [1.0] * k  # default: equal split
    wsum = sum(weights)
    if wsum <= 0:
        print("error: --split weights must sum to > 0", file=sys.stderr)
        return 2

    total = sum(observed)
    expected = [w / wsum * total for w in weights]
    if any(e <= 0 for e in expected):
        print("error: every arm's expected count must be > 0 (check the split)", file=sys.stderr)
        return 2

    chi2 = sum((o - e) ** 2 / e for o, e in zip(observed, expected))
    dof = k - 1
    p_value = _chi2_sf(chi2, dof)

    print("Sample-Ratio-Mismatch (SRM) check — chi-square goodness-of-fit")
    print(f"  arms                 : {k}  (dof = {dof})")
    print(f"  total observed       : {total:,.0f}")
    print("  arm | observed | expected | intended share")
    print("  ----+----------+----------+---------------")
    for i, (o, e, w) in enumerate(zip(observed, expected, weights)):
        print(f"  {i:>3} | {o:>8,.0f} | {e:>8,.1f} | {w / wsum:>13.4%}")
    print(f"  chi-square statistic : {chi2:.4f}")
    print(f"  p-value              : {p_value:.6f}")
    print(f"  alarm threshold      : p < {args.threshold:g}")
    if p_value < args.threshold:
        print("  → SRM DETECTED: the split is broken. The result is INVALID regardless of")
        print("    significance — fix assignment/exposure logging and re-run. Do NOT read")
        print("    the metric (CLAUDE.md §3 #3).")
        return 1
    print("  → no SRM: the observed split is consistent with the intended ratio.")
    print("    (Necessary, not sufficient — also confirm exposure logging + no peeking.)")
    return 0


def _chi2_sf(x: float, dof: int) -> float:
    """Upper-tail survival function of the chi-square distribution.

    Uses the regularized upper incomplete gamma Q(dof/2, x/2) via a series /
    continued-fraction split (Numerical Recipes shape). Stdlib-only (math.lgamma).
    """
    if x <= 0:
        return 1.0
    a = dof / 2.0
    xx = x / 2.0
    if xx < a + 1.0:
        # Lower incomplete via series; SF = 1 - P.
        term = 1.0 / a
        total = term
        n = a
        for _ in range(1000):
            n += 1.0
            term *= xx / n
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        p_lower = total * math.exp(-xx + a * math.log(xx) - math.lgamma(a))
        return max(0.0, 1.0 - p_lower)
    # Upper incomplete via Lentz continued fraction → Q directly.
    tiny = 1e-300
    b = xx + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    q = h * math.exp(-xx + a * math.log(xx) - math.lgamma(a))
    return min(1.0, max(0.0, q))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="experiment_calc.py",
        description="A/B-test design calculator (stdlib only). Sizes the apparatus "
        "(N / MDE / power) and runs the SRM trustworthiness gate. Significance / the "
        "'is the lift real' verdict belongs to applied-statistics — see the module docstring.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    ss = sub.add_parser("sample-size", help="per-arm sample size for a target MDE")
    ss.add_argument("--baseline", type=_parse_rate, required=True,
                    help="baseline conversion rate (e.g. 5%% or 0.05)")
    ss.add_argument("--mde", type=_parse_effect, required=True,
                    help="minimum detectable effect: '0.5pp' (absolute), '10%%' (relative), "
                    "or a bare fraction")
    ss.add_argument("--relative", action="store_true",
                    help="interpret a bare/%%  --mde as a RELATIVE lift on the baseline")
    ss.add_argument("--alpha", type=float, default=0.05, help="two-sided significance (default 0.05)")
    ss.add_argument("--power", type=_parse_rate, default=0.8, help="target power (default 80%%)")
    ss.add_argument("--daily-traffic", type=float, default=None,
                    help="eligible users/day across both arms — adds a duration estimate")
    ss.set_defaults(func=cmd_sample_size)

    md = sub.add_parser("mde", help="smallest detectable effect at a fixed sample")
    md.add_argument("--baseline", type=_parse_rate, required=True, help="baseline conversion rate")
    md.add_argument("--per-arm", type=int, required=True, help="fixed per-arm sample size")
    md.add_argument("--alpha", type=float, default=0.05, help="two-sided significance (default 0.05)")
    md.add_argument("--power", type=_parse_rate, default=0.8, help="target power (default 80%%)")
    md.set_defaults(func=cmd_mde)

    pw = sub.add_parser("power", help="achieved power at a given sample + effect")
    pw.add_argument("--baseline", type=_parse_rate, required=True, help="baseline conversion rate")
    pw.add_argument("--mde", type=_parse_effect, required=True,
                    help="effect to detect: '0.4pp', '10%%', or a bare fraction")
    pw.add_argument("--relative", action="store_true",
                    help="interpret a bare --mde as a RELATIVE lift")
    pw.add_argument("--per-arm", type=int, required=True, help="per-arm sample size")
    pw.add_argument("--alpha", type=float, default=0.05, help="two-sided significance (default 0.05)")
    pw.set_defaults(func=cmd_power)

    sr = sub.add_parser("srm", help="sample-ratio-mismatch chi-square check")
    sr.add_argument("--observed", type=float, nargs="+", required=True,
                    help="observed counts per arm, e.g. --observed 10243 9684")
    sr.add_argument("--split", type=float, nargs="+", default=None,
                    help="intended weights per arm (default equal), e.g. --split 50 50")
    sr.add_argument("--threshold", type=float, default=0.001,
                    help="p-value alarm threshold (default 0.001, the industry SRM norm)")
    sr.set_defaults(func=cmd_srm)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
