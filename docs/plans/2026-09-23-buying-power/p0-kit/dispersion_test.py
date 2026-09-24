#!/usr/bin/env python3
"""P0a dispersion test — the corrected statistic from plan.md's P0a section.

Implements EXACTLY the model pre-registered in preregistration-template.md:

  outcome:    log(effective unit price)
  predictors: log(volume), term length, contract year, channel (direct/reseller/co-op),
              product fixed effects
  noise floor: estimated from >=10 contracts independently double-normalized
  statistic:  noise-corrected residual P75/P25 = exp(1.349 * sqrt(resid_var - noise_var))
  CI:         90%, bootstrap, stratified within product

Why this exists and why it is not the naive test: a raw, uncorrected P75/P25 >= 1.20 passes
42-78% of the time even when TRUE residual dispersion is only 1.05, purely from legitimate
volume/term/channel effects and normalization noise (measured in the FORGE red-team pass on
this plan). This script implements the corrected version so the go/pivot/stop decision rests
on something that could actually come out either way.

Stdlib-only (no numpy/pandas/scipy dependency) — matches this repo's portability convention;
this needs to run on whatever machine Matt has, not a provisioned data-science environment.

Usage:
    python3 dispersion_test.py --contracts contracts.csv --noise-pairs noise_pairs.csv
    python3 dispersion_test.py --self-test

contracts.csv columns (header required):
    product, unit_price, volume, term_months, contract_year, channel
    channel in {direct, reseller, coop}

noise_pairs.csv columns (header required) — >=10 DISTINCT contract_ids, each normalized
independently by two people:
    contract_id, person, log_unit_price
    (exactly 2 rows per contract_id)
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
import sys
from collections import defaultdict

Z75_MINUS_Z25 = 1.3489795  # Phi^-1(0.75) - Phi^-1(0.25), the log-normal P75/P25 multiplier


# ── tiny pure-python linear algebra (OLS via normal equations) ──────────────────────────


def _matmul(a, b):
    n, k = len(a), len(a[0])
    k2, m = len(b), len(b[0])
    assert k == k2, "matmul dimension mismatch"
    out = [[0.0] * m for _ in range(n)]
    for i in range(n):
        ai = a[i]
        for p in range(k):
            aip = ai[p]
            if aip == 0.0:
                continue
            bp = b[p]
            row = out[i]
            for j in range(m):
                row[j] += aip * bp[j]
    return out


def _transpose(a):
    return [list(row) for row in zip(*a)]


def _invert(a):
    """Gauss-Jordan inverse of a square matrix, pure python. Small matrices only (<20x20)."""
    n = len(a)
    aug = [list(a[i]) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot_row][col]) < 1e-12:
            raise ValueError(
                "singular design matrix — check for collinear/degenerate predictors "
                "(e.g. a channel or product category with zero variation)"
            )
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        piv = aug[col][col]
        aug[col] = [x / piv for x in aug[col]]
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            if factor == 0.0:
                continue
            aug[r] = [aug[r][k] - factor * aug[col][k] for k in range(2 * n)]
    return [row[n:] for row in aug]


def ols_fit(X, y):
    """Return (coefficients, residuals, fitted_values) for y ~ X (X includes intercept col)."""
    Xt = _transpose(X)
    XtX = _matmul(Xt, X)
    XtX_inv = _invert(XtX)
    Xty = _matmul(Xt, [[v] for v in y])
    beta = _matmul(XtX_inv, Xty)
    beta = [b[0] for b in beta]
    fitted = [sum(X[i][j] * beta[j] for j in range(len(beta))) for i in range(len(X))]
    resid = [y[i] - fitted[i] for i in range(len(y))]
    return beta, resid, fitted


# ── design matrix construction ───────────────────────────────────────────────────────────


def build_design(rows, sensitivity=False):
    """rows: list of dicts with product/unit_price/volume/term_months/contract_year/channel
    (+ optional fiscal_year_end_days when sensitivity=True).
    Returns (X, y, product_of_row) with product + channel fixed effects (dummy-coded,
    first alphabetical category of each dropped as baseline).
    """
    products = sorted({r["product"] for r in rows})
    channels = sorted({r["channel"] for r in rows})
    if len(products) < 1:
        raise ValueError("no products found in contracts data")
    base_product, base_channel = products[0], channels[0]
    years = [float(r["contract_year"]) for r in rows]
    year_center = statistics.mean(years) if years else 0.0

    X, y, prod_of_row = [], [], []
    for r in rows:
        volume = float(r["volume"])
        if volume <= 0:
            raise ValueError(f"non-positive volume in row: {r}")
        price = float(r["unit_price"])
        if price <= 0:
            raise ValueError(f"non-positive unit_price in row: {r}")
        row = [
            1.0,
            math.log(volume),
            float(r["term_months"]),
            float(r["contract_year"]) - year_center,
        ]
        for p in products[1:]:
            row.append(1.0 if r["product"] == p else 0.0)
        for c in channels[1:]:
            row.append(1.0 if r["channel"] == c else 0.0)
        if sensitivity:
            row.append(float(r.get("fiscal_year_end_days", 0.0)))
        X.append(row)
        y.append(math.log(price))
        prod_of_row.append(r["product"])
    return (
        X,
        y,
        prod_of_row,
        {
            "products": products,
            "channels": channels,
            "base_product": base_product,
            "base_channel": base_channel,
        },
    )


# ── noise floor ───────────────────────────────────────────────────────────────────────────


def estimate_noise_variance(pair_rows):
    """pair_rows: list of dicts {contract_id, person, log_unit_price}. Exactly 2 rows per id.
    sigma_m^2 = Var(diff) / 2, where diff = log_price_person1 - log_price_person2 per contract.
    """
    by_id = defaultdict(list)
    for r in pair_rows:
        by_id[r["contract_id"]].append(float(r["log_unit_price"]))
    diffs = []
    for cid, vals in by_id.items():
        if len(vals) != 2:
            raise ValueError(
                f"noise-pairs contract_id {cid!r} does not have exactly 2 normalizations "
                f"(found {len(vals)}) — every id must be normalized by exactly 2 people"
            )
        diffs.append(vals[0] - vals[1])
    if len(diffs) < 10:
        raise ValueError(
            f"only {len(diffs)} double-normalized contracts found; plan.md requires >= 10 "
            "to estimate the noise floor"
        )
    # population variance of the diffs (ddof=0 is fine here; this is a floor estimate, not inference)
    var_diff = statistics.pvariance(diffs) if len(diffs) > 1 else 0.0
    return var_diff / 2.0, len(diffs)


# ── the corrected statistic ──────────────────────────────────────────────────────────────


def corrected_ratio(residual_variance, noise_variance):
    """exp(1.349 * sqrt(max(0, resid_var - noise_var))). Floors at 0 (never negative under the
    sqrt) and reports whether the floor was hit, since a hit floor means the noise estimate
    consumed all or more than the measured residual spread -- a real, reportable finding,
    not a bug to hide.
    """
    corrected_var = residual_variance - noise_variance
    hit_floor = corrected_var < 0
    corrected_var = max(0.0, corrected_var)
    return math.exp(Z75_MINUS_Z25 * math.sqrt(corrected_var)), hit_floor


def raw_p75_p25(prices):
    """Uncorrected ratio for the same-model comparison plan.md item 4 asks to report alongside."""
    s = sorted(prices)
    n = len(s)
    if n < 4:
        return float("nan")

    def pct(p):
        idx = p * (n - 1)
        lo, hi = int(math.floor(idx)), int(math.ceil(idx))
        if lo == hi:
            return s[lo]
        frac = idx - lo
        return s[lo] * (1 - frac) + s[hi] * frac

    p25, p75 = pct(0.25), pct(0.75)
    if p25 <= 0:
        return float("nan")
    return p75 / p25


# ── bootstrap, stratified within product ─────────────────────────────────────────────────


def bootstrap_ci(rows, noise_variance, n_boot=2000, seed=1234, sensitivity=False):
    rng = random.Random(seed)
    by_product = defaultdict(list)
    for r in rows:
        by_product[r["product"]].append(r)

    pooled_stats = []
    per_product_stats = defaultdict(list)

    for _ in range(n_boot):
        sample = []
        for _prod, prod_rows in by_product.items():
            n = len(prod_rows)
            sample.extend(prod_rows[rng.randrange(n)] for _ in range(n))
        try:
            X, y, prod_of_row, _meta = build_design(sample, sensitivity=sensitivity)
            _beta, resid, _fitted = ols_fit(X, y)
        except ValueError:
            continue  # a degenerate resample (e.g. a product/channel dropped entirely) -> skip
        resid_var = statistics.pvariance(resid) if len(resid) > 1 else 0.0
        stat, _ = corrected_ratio(resid_var, noise_variance)
        pooled_stats.append(stat)

        by_prod_resid = defaultdict(list)
        for p, e in zip(prod_of_row, resid):
            by_prod_resid[p].append(e)
        for p, es in by_prod_resid.items():
            if len(es) > 1:
                v = statistics.pvariance(es)
                s, _ = corrected_ratio(v, noise_variance)
                per_product_stats[p].append(s)

    def ci90(vals):
        if not vals:
            return (float("nan"), float("nan"))
        s = sorted(vals)
        n = len(s)
        lo = s[max(0, int(0.05 * n))]
        hi = s[min(n - 1, int(0.95 * n))]
        return (lo, hi)

    return ci90(pooled_stats), {p: ci90(v) for p, v in per_product_stats.items()}


# ── main analysis ─────────────────────────────────────────────────────────────────────────


def run_analysis(contract_rows, noise_pair_rows, sensitivity=False, n_boot=2000, seed=1234):
    noise_var, n_pairs = estimate_noise_variance(noise_pair_rows)

    X, y, prod_of_row, meta = build_design(contract_rows, sensitivity=sensitivity)
    beta, resid, fitted = ols_fit(X, y)
    resid_var_pooled = statistics.pvariance(resid) if len(resid) > 1 else 0.0

    by_prod_resid = defaultdict(list)
    by_prod_price = defaultdict(list)
    for p, e in zip(prod_of_row, resid):
        by_prod_resid[p].append(e)
    for r in contract_rows:
        by_prod_price[r["product"]].append(float(r["unit_price"]))

    pooled_stat, pooled_hit_floor = corrected_ratio(resid_var_pooled, noise_var)
    per_product_point = {
        p: corrected_ratio(statistics.pvariance(es) if len(es) > 1 else 0.0, noise_var)
        for p, es in by_prod_resid.items()
    }
    (pooled_ci_lo, pooled_ci_hi), per_product_ci = bootstrap_ci(
        contract_rows, noise_var, n_boot=n_boot, seed=seed, sensitivity=sensitivity
    )
    raw_ratio_pooled = raw_p75_p25([float(r["unit_price"]) for r in contract_rows])
    raw_ratio_by_product = {p: raw_p75_p25(prices) for p, prices in by_prod_price.items()}

    n_at_or_above_110 = sum(1 for stat, _ in per_product_point.values() if stat >= 1.10)

    return {
        "n_contracts": len(contract_rows),
        "n_products": len(meta["products"]),
        "products": meta["products"],
        "noise_variance": noise_var,
        "n_noise_pairs": n_pairs,
        "pooled": {
            "residual_variance": resid_var_pooled,
            "corrected_statistic": pooled_stat,
            "hit_zero_floor": pooled_hit_floor,
            "ci90_lower": pooled_ci_lo,
            "ci90_upper": pooled_ci_hi,
            "raw_p75_p25": raw_ratio_pooled,
        },
        "per_product": {
            p: {
                "n": len(by_prod_resid[p]),
                "corrected_statistic": per_product_point[p][0],
                "hit_zero_floor": per_product_point[p][1],
                "ci90_lower": per_product_ci.get(p, (float("nan"), float("nan")))[0],
                "ci90_upper": per_product_ci.get(p, (float("nan"), float("nan")))[1],
                "raw_p75_p25": raw_ratio_by_product.get(p, float("nan")),
            }
            for p in meta["products"]
        },
        "acceptance_check_a": {
            "criterion": "pooled 90% CI lower bound >= 1.10 AND point estimate >= 1.10 in >= 2 products",
            "pooled_ci_lower_meets_threshold": pooled_ci_lo >= 1.10,
            "n_products_at_or_above_1_10": n_at_or_above_110,
            "n_products_required": 2,
            "PASSES": (pooled_ci_lo >= 1.10)
            and (n_at_or_above_110 >= min(2, len(meta["products"]))),
        },
    }


def _print_report(result):
    print(
        f"Contracts analyzed: {result['n_contracts']} across {result['n_products']} product(s): "
        f"{', '.join(result['products'])}"
    )
    print(
        f"Noise floor: variance={result['noise_variance']:.5f} "
        f"(from {result['n_noise_pairs']} double-normalized contracts)"
    )
    print()
    p = result["pooled"]
    print("POOLED:")
    print(f"  residual variance:        {p['residual_variance']:.5f}")
    print(
        f"  corrected P75/P25:        {p['corrected_statistic']:.3f}"
        + (
            "  [HIT ZERO FLOOR — noise estimate >= measured residual spread]"
            if p["hit_zero_floor"]
            else ""
        )
    )
    print(f"  90% bootstrap CI:         [{p['ci90_lower']:.3f}, {p['ci90_upper']:.3f}]")
    print(
        f"  raw (uncorrected) P75/P25: {p['raw_p75_p25']:.3f}   <- for comparison only, not the gate"
    )
    print()
    print("PER PRODUCT:")
    for name, pp in result["per_product"].items():
        print(
            f"  {name}: n={pp['n']}  corrected={pp['corrected_statistic']:.3f}"
            + ("  [FLOORED]" if pp["hit_zero_floor"] else "")
            + f"  CI=[{pp['ci90_lower']:.3f}, {pp['ci90_upper']:.3f}]"
            + f"  raw={pp['raw_p75_p25']:.3f}"
        )
    print()
    a = result["acceptance_check_a"]
    print("Acceptance criterion (a) from plan.md P0a — dispersion only, NOT the full GO decision:")
    print(f"  {a['criterion']}")
    print(f"  pooled CI lower >= 1.10:  {a['pooled_ci_lower_meets_threshold']}")
    print(
        f"  products >= 1.10:        {a['n_products_at_or_above_1_10']} of "
        f"{result['n_products']} (need >= {a['n_products_required']})"
    )
    print(f"  => criterion (a): {'PASSES' if a['PASSES'] else 'DOES NOT PASS'}")
    print()
    print("Reminder: criterion (a) is ONE of six required conditions (a)-(f) for a provisional GO.")
    print(
        "This script does not and cannot evaluate (b) seedability, (c) demand, (d) the TEC finding,"
    )
    print("(e) incumbent coverage, or (f) runway -- those need the interview/research results.")


def _read_csv(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ── self-test ─────────────────────────────────────────────────────────────────────────────


def self_test():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(f"  {'OK  ' if cond else 'FAIL'} {name}")
        if not cond:
            ok = False

    rng = random.Random(42)
    true_sigma = 0.10  # target residual sigma s.t. exp(1.349*0.10) ~= 1.145
    noise_sigma = 0.05
    products = ["ProdA", "ProdB", "ProdC"]
    channels = ["direct", "reseller", "coop"]
    rows = []
    for prod in products:
        base_price = {"ProdA": 100.0, "ProdB": 50.0, "ProdC": 200.0}[prod]
        for _i in range(20):
            volume = rng.choice([10, 25, 50, 100, 250, 500])
            term = rng.choice([12, 24, 36])
            year = rng.choice([2023, 2024, 2025, 2026])
            channel = rng.choice(channels)
            volume_effect = -0.15 * math.log(volume / 100.0)
            channel_effect = {"direct": 0.0, "reseller": 0.03, "coop": -0.04}[channel]
            true_noise = rng.gauss(0, true_sigma)
            measurement_noise = rng.gauss(0, noise_sigma)
            log_price = (
                math.log(base_price)
                + volume_effect
                + channel_effect
                + true_noise
                + measurement_noise
            )
            rows.append(
                {
                    "product": prod,
                    "unit_price": math.exp(log_price),
                    "volume": volume,
                    "term_months": term,
                    "contract_year": year,
                    "channel": channel,
                }
            )

    # build noise-pairs: re-normalize 12 of the same contracts with fresh measurement noise
    pair_rows = []
    for i, r in enumerate(rows[:12]):
        true_component = math.log(r["unit_price"]) - rng.gauss(0, noise_sigma)  # approx backout
        pair_rows.append(
            {
                "contract_id": f"c{i}",
                "person": "A",
                "log_unit_price": true_component + rng.gauss(0, noise_sigma),
            }
        )
        pair_rows.append(
            {
                "contract_id": f"c{i}",
                "person": "B",
                "log_unit_price": true_component + rng.gauss(0, noise_sigma),
            }
        )

    noise_var, n_pairs = estimate_noise_variance(pair_rows)
    chk("noise variance estimated and positive", noise_var > 0)
    chk("n_pairs == 12", n_pairs == 12)

    result = run_analysis(rows, pair_rows, n_boot=300, seed=7)
    expected_stat = math.exp(Z75_MINUS_Z25 * true_sigma)  # ~= 1.145
    got = result["pooled"]["corrected_statistic"]
    chk(
        f"corrected statistic near expected ({expected_stat:.3f}, got {got:.3f})",
        abs(got - expected_stat) < 0.25,
    )
    chk(
        "raw ratio differs from corrected (noise/covariates matter)",
        abs(result["pooled"]["raw_p75_p25"] - got) > 0.001,
    )
    chk("acceptance_check_a structure present", "PASSES" in result["acceptance_check_a"])
    chk("per-product results for all 3 products", len(result["per_product"]) == 3)

    # teeth: a dataset with genuinely near-zero true dispersion should NOT falsely pass at high rate
    # (mirrors the red-team's own simulation: this is a spot-check, not the full power study)
    flat_rows = []
    for prod in products:
        base_price = {"ProdA": 100.0, "ProdB": 50.0, "ProdC": 200.0}[prod]
        for _i in range(20):
            volume = rng.choice([10, 25, 50, 100, 250, 500])
            term = rng.choice([12, 24, 36])
            year = rng.choice([2023, 2024, 2025, 2026])
            channel = rng.choice(channels)
            volume_effect = -0.15 * math.log(volume / 100.0)
            channel_effect = {"direct": 0.0, "reseller": 0.03, "coop": -0.04}[channel]
            measurement_noise = rng.gauss(0, noise_sigma)
            log_price = math.log(base_price) + volume_effect + channel_effect + measurement_noise
            flat_rows.append(
                {
                    "product": prod,
                    "unit_price": math.exp(log_price),
                    "volume": volume,
                    "term_months": term,
                    "contract_year": year,
                    "channel": channel,
                }
            )
    flat_result = run_analysis(flat_rows, pair_rows, n_boot=300, seed=7)
    chk(
        "near-zero true dispersion does not falsely clear the CI-lower-bound threshold",
        flat_result["pooled"]["ci90_lower"] < 1.10,
    )

    print()
    print("SELF-TEST " + ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--contracts", help="path to contracts.csv")
    ap.add_argument("--noise-pairs", help="path to noise_pairs.csv")
    ap.add_argument(
        "--sensitivity",
        action="store_true",
        help="include fiscal_year_end_days as a sensitivity predictor",
    )
    ap.add_argument("--n-boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=1234)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if not args.contracts or not args.noise_pairs:
        ap.error("--contracts and --noise-pairs are required (or pass --self-test)")

    contract_rows = _read_csv(args.contracts)
    noise_rows = _read_csv(args.noise_pairs)
    if len(contract_rows) < 4:
        print(
            "ERROR: fewer than 4 contracts provided — cannot compute percentiles meaningfully.",
            file=sys.stderr,
        )
        return 1
    try:
        result = run_analysis(
            contract_rows,
            noise_rows,
            sensitivity=args.sensitivity,
            n_boot=args.n_boot,
            seed=args.seed,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    _print_report(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
