#!/usr/bin/env python3
"""drift_check.py - a zero-dependency feature-drift calculator.

Removes arithmetic error from the recurring monitoring decision an
ml-monitoring-engineer runs constantly: "has this feature's distribution
drifted enough to investigate or retrain?" It computes the standard
no-labels-needed drift statistics on a *reference* (training) sample vs. a
*current* (production) sample:

  psi   Population Stability Index on a numerical feature. Bins the reference
        distribution (quantile or equal-width), maps the current sample into
        those bins, and sums (p_cur - p_ref) * ln(p_cur / p_ref). Prints the
        per-bin contributions and the standard verdict bands. Pairs with the
        "which drift metric" tree (knowledge/ml-engineering-decision-trees.md).

  ks    Two-sample Kolmogorov-Smirnov statistic (the max gap between the two
        empirical CDFs) on a numerical feature, plus the approximate critical
        value at a chosen alpha. Detects a shift in shape/location with no
        binning choice. Pairs with the same tree.

  chi2  Chi-squared statistic on a CATEGORICAL feature: compares observed
        current category counts against the counts expected from the reference
        proportions. Prints the statistic and degrees of freedom. Pairs with
        the categorical branch of the "which drift metric" tree.

This is a CALCULATOR, not a monitoring system - it does not fetch data, store
state, fire alerts, or decide a retrain. The user supplies both samples; the
tool does the arithmetic and shows the formula and the conventional band.
Stdlib only (argparse, math); runs anywhere Python 3.8+ is present.

IMPORTANT: the verdict bands (PSI <0.1 stable / 0.1-0.2 moderate / >0.2
significant; the KS critical-value approximation; chi-squared significance)
are CONVENTIONS and approximations, not a substitute for a statistician. Per
the team's house opinions (../CLAUDE.md S2), whether a measured drift or a
downstream performance change is statistically *real* routes to
applied-statistics. A drift signal maps to "investigate", not automatically to
"retrain" - see best-practices/monitor-drift-and-define-the-trigger.md.

Examples
--------
  # PSI on a numerical feature, 10 quantile bins
  python3 drift_check.py psi --reference ref.txt --current cur.txt --bins 10

  # PSI from inline comma-separated values
  python3 drift_check.py psi --ref-values "1,2,3,4,5,6" --cur-values "4,5,6,7,8,9"

  # KS two-sample test at alpha=0.05
  python3 drift_check.py ks --reference ref.txt --current cur.txt --alpha 0.05

  # Chi-squared on a categorical feature (label:count pairs)
  python3 drift_check.py chi2 --ref-counts "a:50,b:30,c:20" --cur-counts "a:20,b:30,c:50"

Each value file is one number per line (or one category token per line for
chi2). Inline flags override file inputs.
"""

from __future__ import annotations

import argparse
import math
import sys
from collections import Counter
from collections.abc import Sequence

# A small floor so an empty bin can't produce a log(0)/div-by-0 in the PSI sum.
# This is the standard PSI smoothing convention; it is documented, not hidden.
_EPS = 1e-6


def _read_numbers(path: str) -> list[float]:
    """Read one float per non-blank line. Raises ValueError on a bad token."""
    out: list[float] = []
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            tok = raw.strip()
            if not tok:
                continue
            try:
                out.append(float(tok))
            except ValueError as exc:
                raise ValueError(f"{path}:{lineno}: not a number: {tok!r}") from exc
    return out


def _read_tokens(path: str) -> list[str]:
    """Read one category token per non-blank line."""
    out: list[str] = []
    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            tok = raw.strip()
            if tok:
                out.append(tok)
    return out


def _parse_inline_numbers(spec: str) -> list[float]:
    return [float(t.strip()) for t in spec.split(",") if t.strip()]


def _parse_label_counts(spec: str) -> Counter[str]:
    """Parse 'a:50,b:30' into a Counter. Raises ValueError on a bad pair."""
    counts: Counter[str] = Counter()
    for pair in spec.split(","):
        pair = pair.strip()
        if not pair:
            continue
        if ":" not in pair:
            raise ValueError(f"expected 'label:count', got {pair!r}")
        label, _, num = pair.partition(":")
        label = label.strip()
        if not label:
            raise ValueError(f"empty label in {pair!r}")
        counts[label] += int(num.strip())
    return counts


def _quantile_edges(values: Sequence[float], bins: int) -> list[float]:
    """Bin edges at the reference's empirical quantiles (equal-frequency)."""
    ordered = sorted(values)
    n = len(ordered)
    edges = [ordered[0]]
    for i in range(1, bins):
        # position of the i/bins quantile via linear interpolation
        pos = i / bins * (n - 1)
        lo = int(math.floor(pos))
        hi = min(lo + 1, n - 1)
        frac = pos - lo
        edges.append(ordered[lo] + (ordered[hi] - ordered[lo]) * frac)
    edges.append(ordered[-1])
    # Collapse duplicate edges (a spiky reference can produce them) so a bin is
    # never zero-width; PSI degrades gracefully to fewer bins.
    dedup = [edges[0]]
    for e in edges[1:]:
        if e > dedup[-1]:
            dedup.append(e)
    return dedup


def _equal_width_edges(values: Sequence[float], bins: int) -> list[float]:
    lo, hi = min(values), max(values)
    if hi == lo:
        hi = lo + 1.0  # degenerate single-value reference: one usable bin
    width = (hi - lo) / bins
    return [lo + i * width for i in range(bins + 1)]


def _bin_counts(values: Sequence[float], edges: Sequence[float]) -> list[int]:
    """Count values into [edge_i, edge_{i+1}); last bin is closed on the right."""
    nbins = len(edges) - 1
    counts = [0] * nbins
    for v in values:
        if v <= edges[0]:
            counts[0] += 1
            continue
        if v >= edges[-1]:
            counts[-1] += 1
            continue
        # linear scan is fine for a CLI-scale sample; bins are few
        placed = False
        for i in range(nbins):
            if edges[i] <= v < edges[i + 1]:
                counts[i] += 1
                placed = True
                break
        if not placed:
            counts[-1] += 1
    return counts


def compute_psi(
    reference: Sequence[float],
    current: Sequence[float],
    bins: int,
    method: str,
) -> tuple[float, list[dict]]:
    """Return (total_psi, per_bin_detail). per_bin_detail rows carry the math."""
    if method == "quantile":
        edges = _quantile_edges(reference, bins)
    else:
        edges = _equal_width_edges(reference, bins)

    # A constant (or spiky) reference sample can collapse quantile edges down to a
    # single value; guarantee at least two edges so binning and per-bin detail
    # never index past the edge list. PSI then degrades to one bin (contribution 0).
    if len(edges) < 2:
        base = edges[0] if edges else 0.0
        edges = [base, base]

    ref_counts = _bin_counts(reference, edges)
    cur_counts = _bin_counts(current, edges)
    n_ref = sum(ref_counts) or 1
    n_cur = sum(cur_counts) or 1

    total = 0.0
    detail: list[dict] = []
    for i in range(len(ref_counts)):
        p_ref = max(ref_counts[i] / n_ref, _EPS)
        p_cur = max(cur_counts[i] / n_cur, _EPS)
        contrib = (p_cur - p_ref) * math.log(p_cur / p_ref)
        total += contrib
        detail.append(
            {
                "bin": i,
                "range": (edges[i], edges[i + 1]),
                "p_ref": p_ref,
                "p_cur": p_cur,
                "contribution": contrib,
            }
        )
    return total, detail


def psi_band(psi: float) -> str:
    """The conventional PSI interpretation bands (a convention, not a law)."""
    if psi < 0.1:
        return "stable (PSI < 0.1) - no significant population shift"
    if psi < 0.2:
        return "moderate shift (0.1 <= PSI < 0.2) - investigate"
    return "significant shift (PSI >= 0.2) - investigate / candidate to retrain"


def _ecdf_value(ordered: Sequence[float], x: float) -> float:
    """Empirical CDF of `ordered` evaluated at x (fraction of points <= x)."""
    # binary search for the rightmost index with value <= x
    lo, hi = 0, len(ordered)
    while lo < hi:
        mid = (lo + hi) // 2
        if ordered[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo / len(ordered)


def compute_ks(reference: Sequence[float], current: Sequence[float]) -> tuple[float, float]:
    """Two-sample KS statistic D = max|F_ref(x) - F_cur(x)| at all sample points."""
    ref_sorted = sorted(reference)
    cur_sorted = sorted(current)
    d = 0.0
    for x in set(ref_sorted) | set(cur_sorted):
        d = max(d, abs(_ecdf_value(ref_sorted, x) - _ecdf_value(cur_sorted, x)))
    return d, d


def ks_critical(n_ref: int, n_cur: int, alpha: float) -> float:
    """Approximate two-sample KS critical value: c(alpha)*sqrt((n+m)/(n*m)).

    c(alpha) = sqrt(-0.5 * ln(alpha/2)) is the standard large-sample
    approximation. This is an approximation, not an exact p-value - confirm a
    borderline result with a real test (applied-statistics).
    """
    c_alpha = math.sqrt(-0.5 * math.log(alpha / 2.0))
    return c_alpha * math.sqrt((n_ref + n_cur) / (n_ref * n_cur))


def compute_chi2(
    ref_counts: Counter[str], cur_counts: Counter[str]
) -> tuple[float, int, list[dict]]:
    """Chi-squared of current observed counts vs reference-proportion expected."""
    categories = sorted(set(ref_counts) | set(cur_counts))
    n_ref = sum(ref_counts.values()) or 1
    n_cur = sum(cur_counts.values())
    stat = 0.0
    detail: list[dict] = []
    for cat in categories:
        p_ref = ref_counts.get(cat, 0) / n_ref
        expected = max(p_ref * n_cur, _EPS)  # smooth a zero-expected category
        observed = cur_counts.get(cat, 0)
        term = (observed - expected) ** 2 / expected
        stat += term
        detail.append({"category": cat, "observed": observed, "expected": expected, "term": term})
    dof = max(len(categories) - 1, 1)
    return stat, dof, detail


def _fmt_range(rng: tuple[float, float]) -> str:
    return f"[{rng[0]:.4g}, {rng[1]:.4g})"


def cmd_psi(args: argparse.Namespace) -> int:
    if args.ref_values:
        reference = _parse_inline_numbers(args.ref_values)
    elif args.reference:
        reference = _read_numbers(args.reference)
    else:
        print("psi: need --reference FILE or --ref-values CSV", file=sys.stderr)
        return 2
    if args.cur_values:
        current = _parse_inline_numbers(args.cur_values)
    elif args.current:
        current = _read_numbers(args.current)
    else:
        print("psi: need --current FILE or --cur-values CSV", file=sys.stderr)
        return 2
    if not reference or not current:
        print("psi: both samples must be non-empty", file=sys.stderr)
        return 2
    if args.bins < 1:
        print("psi: --bins must be >= 1", file=sys.stderr)
        return 2

    total, detail = compute_psi(reference, current, args.bins, args.method)
    print(f"PSI  (method={args.method}, bins={len(detail)})")
    print(f"  reference n={len(reference)}  current n={len(current)}")
    print("  bin  range                       p_ref    p_cur    contribution")
    for row in detail:
        print(
            f"  {row['bin']:>3}  {_fmt_range(row['range']):<28} "
            f"{row['p_ref']:.4f}   {row['p_cur']:.4f}   {row['contribution']:+.5f}"
        )
    print(f"  ---\n  PSI = {total:.5f}")
    print(f"  verdict: {psi_band(total)}")
    print(
        "  note: a band is a convention; route 'is the downstream change real?'"
        " to applied-statistics, and map drift to investigate, not auto-retrain."
    )
    return 0


def cmd_ks(args: argparse.Namespace) -> int:
    if args.ref_values:
        reference = _parse_inline_numbers(args.ref_values)
    elif args.reference:
        reference = _read_numbers(args.reference)
    else:
        print("ks: need --reference FILE or --ref-values CSV", file=sys.stderr)
        return 2
    if args.cur_values:
        current = _parse_inline_numbers(args.cur_values)
    elif args.current:
        current = _read_numbers(args.current)
    else:
        print("ks: need --current FILE or --cur-values CSV", file=sys.stderr)
        return 2
    if not reference or not current:
        print("ks: both samples must be non-empty", file=sys.stderr)
        return 2

    d, _ = compute_ks(reference, current)
    crit = ks_critical(len(reference), len(current), args.alpha)
    reject = d > crit
    print("KS two-sample")
    print(f"  reference n={len(reference)}  current n={len(current)}")
    print(f"  D (max CDF gap) = {d:.5f}")
    print(f"  approx critical value @ alpha={args.alpha} = {crit:.5f}")
    print(
        f"  verdict: {'D > critical - distributions differ (investigate)' if reject else 'D <= critical - no significant difference at this alpha'}"
    )
    print(
        "  note: this is a large-sample approximation, not an exact p-value;"
        " confirm a borderline result with applied-statistics."
    )
    return 0


def cmd_chi2(args: argparse.Namespace) -> int:
    if args.ref_counts:
        ref_counts = _parse_label_counts(args.ref_counts)
    elif args.reference:
        ref_counts = Counter(_read_tokens(args.reference))
    else:
        print("chi2: need --reference FILE or --ref-counts SPEC", file=sys.stderr)
        return 2
    if args.cur_counts:
        cur_counts = _parse_label_counts(args.cur_counts)
    elif args.current:
        cur_counts = Counter(_read_tokens(args.current))
    else:
        print("chi2: need --current FILE or --cur-counts SPEC", file=sys.stderr)
        return 2
    if not ref_counts or not cur_counts:
        print("chi2: both samples must be non-empty", file=sys.stderr)
        return 2

    stat, dof, detail = compute_chi2(ref_counts, cur_counts)
    print("Chi-squared (categorical drift)")
    print(f"  categories: {len(detail)}  dof={dof}")
    print("  category        observed   expected     term")
    for row in detail:
        print(
            f"  {row['category']:<14} {row['observed']:>8}   "
            f"{row['expected']:>8.2f}   {row['term']:.5f}"
        )
    print(f"  ---\n  chi2 = {stat:.5f}  (dof={dof})")
    print(
        "  note: compare against a chi-squared critical value at your dof/alpha;"
        " a significant stat means category mix shifted - investigate, and route"
        " significance to applied-statistics."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drift_check.py",
        description="Zero-dependency feature-drift calculator (PSI / KS / chi-squared).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_psi = sub.add_parser("psi", help="Population Stability Index (numerical)")
    p_psi.add_argument("--reference", help="reference (training) sample file, one number per line")
    p_psi.add_argument("--current", help="current (production) sample file")
    p_psi.add_argument("--ref-values", help="inline reference values, comma-separated")
    p_psi.add_argument("--cur-values", help="inline current values, comma-separated")
    p_psi.add_argument("--bins", type=int, default=10, help="number of bins (default 10)")
    p_psi.add_argument(
        "--method",
        choices=("quantile", "equal-width"),
        default="quantile",
        help="binning method (default quantile / equal-frequency)",
    )
    p_psi.set_defaults(func=cmd_psi)

    p_ks = sub.add_parser("ks", help="Two-sample Kolmogorov-Smirnov (numerical)")
    p_ks.add_argument("--reference", help="reference sample file")
    p_ks.add_argument("--current", help="current sample file")
    p_ks.add_argument("--ref-values", help="inline reference values, comma-separated")
    p_ks.add_argument("--cur-values", help="inline current values, comma-separated")
    p_ks.add_argument("--alpha", type=float, default=0.05, help="significance level (default 0.05)")
    p_ks.set_defaults(func=cmd_ks)

    p_chi2 = sub.add_parser("chi2", help="Chi-squared (categorical)")
    p_chi2.add_argument("--reference", help="reference tokens file, one category per line")
    p_chi2.add_argument("--current", help="current tokens file")
    p_chi2.add_argument("--ref-counts", help="inline reference 'label:count,...'")
    p_chi2.add_argument("--cur-counts", help="inline current 'label:count,...'")
    p_chi2.set_defaults(func=cmd_chi2)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
