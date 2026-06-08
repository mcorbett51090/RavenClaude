#!/usr/bin/env python3
"""ds_calc.py — a zero-dependency data-science-research evaluation calculator.

Removes arithmetic error from three recurring "did I score this honestly?" checks an
exploratory data scientist / modeling engineer runs constantly — WITHOUT pulling in
numpy / pandas / scikit-learn, so it runs anywhere Python 3.8+ is present. It is a
CALCULATOR, not a data source: the user supplies every count / value; the tool does the
arithmetic and shows the formula. It does not load a dataset, fit a model, or fetch a
benchmark.

  classification-metrics
               Precision / recall / F1 / accuracy from a confusion matrix.
                 precision = tp / (tp + fp)        (of predicted-positive, how many right)
                 recall    = tp / (tp + fn)        (of actual-positive, how many caught)
                 F1        = 2*P*R / (P + R)        (harmonic mean of P and R)
                 accuracy  = (tp + tn) / (tp+fp+fn+tn)
               Reports specificity and the positive base rate too, and WARNS when the
               classes are imbalanced — because accuracy on a rare-positive problem
               measures the base rate, not skill (the metric-must-match-the-decision rule;
               see scenarios/2026-06-08-accuracy-lied-on-imbalanced-fraud.md).

  regression-metrics
               MAE / RMSE / R2 from paired y_true / y_pred lists.
                 MAE  = mean(|y_true - y_pred|)
                 RMSE = sqrt(mean((y_true - y_pred)^2))
                 R2   = 1 - SS_res/SS_tot,  SS_tot = sum((y_true - mean(y_true))^2)
               Reports the mean-baseline RMSE (predict the column mean) alongside the
               model RMSE so a model that "barely beats the mean" is visible — the
               baseline-before-the-fanciest-model rule (R2 <= 0 means worse than the mean;
               see scenarios/2026-06-08-deep-net-that-couldnt-beat-the-mean.md).

  split-check  Train / val / test split sanity. Confirms the three fractions sum to 1.0,
               flags any split smaller than a --min-frac floor, and — given the per-split
               positive-class counts — WARNS when class balance drifts across splits or a
               split is so small the rare class may be absent (the stratification check the
               split-before-you-touch-the-data rule depends on).

This is decision-support, not a substitute for a real evaluation: validate every figure
against the engagement's actual data, report the metric WITH its uncertainty (cross-
validate; a single split lies), and confirm no leakage before trusting any score.

Examples
--------
  # P/R/F1/accuracy for a fraud model: 60 caught, 12 false alarms, 40 missed, 9888 clean
  python3 ds_calc.py classification-metrics --tp 60 --fp 12 --fn 40 --tn 9888

  # MAE/RMSE/R2 for 5 predictions vs truth
  python3 ds_calc.py regression-metrics \\
      --y-true 3.0 -0.5 2.0 7.0 4.2 --y-pred 2.5 0.0 2.1 7.8 4.0

  # 70/15/15 split, with positive counts per split to check class balance
  python3 ds_calc.py split-check --train 0.7 --val 0.15 --test 0.15 \\
      --n 10000 --pos-train 49 --pos-val 11 --pos-test 10
"""

from __future__ import annotations

import argparse
import math
import sys

# A split whose positive-class count is below this is too small to trust the
# class balance / stratification on.
_MIN_MINORITY_COUNT = 10
# Relative drift in positive rate across splits above this is flagged.
_BALANCE_DRIFT_REL = 0.30


def _imbalance_note(pos_rate: float) -> str:
    minority = min(pos_rate, 1.0 - pos_rate)
    if minority < 0.05:
        return "SEVERE imbalance (minority < 5%) — accuracy measures the base rate, not skill"
    if minority < 0.20:
        return "imbalanced (minority < 20%) — prefer precision/recall/F1 over accuracy"
    return "roughly balanced"


def cmd_classification_metrics(args: argparse.Namespace) -> int:
    tp, fp, fn, tn = args.tp, args.fp, args.fn, args.tn
    for name, v in (("--tp", tp), ("--fp", fp), ("--fn", fn), ("--tn", tn)):
        if v < 0:
            print(f"error: {name} must be >= 0, got {v}", file=sys.stderr)
            return 2
    total = tp + fp + fn + tn
    if total == 0:
        print("error: the confusion matrix is all zeros — nothing to score", file=sys.stderr)
        return 2

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / total
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    pos_rate = (tp + fn) / total

    print("Classification metrics — from confusion matrix")
    print(f"  confusion matrix : tp={tp}  fp={fp}  fn={fn}  tn={tn}  (n={total:,})")
    print(f"  positive base rate: {pos_rate:.4f}  ({_imbalance_note(pos_rate)})")
    print(f"  precision        : {precision:.4f}   = tp/(tp+fp)")
    print(f"  recall (TPR)     : {recall:.4f}   = tp/(tp+fn)")
    print(f"  specificity (TNR): {specificity:.4f}   = tn/(tn+fp)")
    print(f"  F1               : {f1:.4f}   = 2*P*R/(P+R)")
    print(f"  accuracy         : {accuracy:.4f}   = (tp+tn)/n")
    if min(pos_rate, 1.0 - pos_rate) < 0.20:
        print("  WARNING: accuracy is misleading here — a constant predictor scores "
              f"{max(pos_rate, 1.0 - pos_rate):.4f}. Choose the metric from the decision "
              "(precision/recall at the deployment threshold), not accuracy.")
    if (tp + fp) == 0:
        print("  note: no positive predictions — precision is undefined; reported as 0.")
    print("  reminder: one split has no error bar — cross-validate and report the spread.")
    return 0


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def cmd_regression_metrics(args: argparse.Namespace) -> int:
    y_true, y_pred = args.y_true, args.y_pred
    if len(y_true) != len(y_pred):
        print(f"error: --y-true ({len(y_true)}) and --y-pred ({len(y_pred)}) must be the "
              "same length", file=sys.stderr)
        return 2
    n = len(y_true)
    if n == 0:
        print("error: need at least one (y_true, y_pred) pair", file=sys.stderr)
        return 2

    residuals = [t - p for t, p in zip(y_true, y_pred)]
    mae = _mean([abs(r) for r in residuals])
    mse = _mean([r * r for r in residuals])
    rmse = math.sqrt(mse)
    ybar = _mean(y_true)
    ss_res = sum(r * r for r in residuals)
    ss_tot = sum((t - ybar) ** 2 for t in y_true)
    baseline_rmse = math.sqrt(_mean([(t - ybar) ** 2 for t in y_true]))

    print("Regression metrics — from paired y_true / y_pred")
    print(f"  n pairs          : {n}")
    print(f"  MAE              : {mae:.4f}   = mean(|y_true - y_pred|)")
    print(f"  RMSE             : {rmse:.4f}   = sqrt(mean((y_true - y_pred)^2))")
    print(f"  mean-baseline RMSE: {baseline_rmse:.4f}   = RMSE of predicting mean(y_true) = {ybar:.4f}")
    if ss_tot == 0:
        print("  R2               : undefined — y_true is constant (SS_tot = 0), so there is "
              "no variance to explain.")
    else:
        r2 = 1.0 - ss_res / ss_tot
        print(f"  R2               : {r2:.4f}   = 1 - SS_res/SS_tot")
        if r2 <= 0.0:
            print("  WARNING: R2 <= 0 — the model is no better than (or worse than) predicting "
                  "the column mean. Establish a baseline before the fanciest model.")
        elif rmse >= baseline_rmse:
            print("  WARNING: RMSE does not beat the mean-baseline RMSE — a fancy model that "
                  "barely beats the mean is a finding about the data, not a win.")
    print("  reminder: report this WITH its uncertainty (cross-validate; a single split lies).")
    return 0


def cmd_split_check(args: argparse.Namespace) -> int:
    train, val, test = args.train, args.val, args.test
    for name, v in (("--train", train), ("--val", val), ("--test", test)):
        if not 0.0 <= v <= 1.0:
            print(f"error: {name} must be in [0, 1], got {v}", file=sys.stderr)
            return 2
    total = train + val + test
    print("Split check — train / val / test")
    print(f"  fractions        : train={train:g}  val={val:g}  test={test:g}  (sum={total:.4f})")
    if abs(total - 1.0) > 1e-6:
        print(f"  WARNING: fractions sum to {total:.4f}, not 1.0 — the split does not "
              "partition the data.")
    for name, v in (("train", train), ("val", val), ("test", test)):
        if 0.0 < v < args.min_frac:
            print(f"  WARNING: {name} fraction {v:g} is below --min-frac {args.min_frac:g} — "
                  "this split may be too small to evaluate on.")

    pos = (args.pos_train, args.pos_val, args.pos_test)
    if args.n is not None and any(p is not None for p in pos):
        if args.n <= 0:
            print("error: --n must be > 0 when checking class balance", file=sys.stderr)
            return 2
        names = ("train", "val", "test")
        fracs = (train, val, test)
        rates: list[tuple[str, float, int, int]] = []
        print("  class balance    :")
        for name, frac, p in zip(names, fracs, pos):
            if p is None:
                continue
            split_n = round(frac * args.n)
            if p < 0 or p > split_n:
                print(f"error: pos-{name} ({p}) must be in [0, {split_n}] "
                      f"(= round({frac:g} * {args.n}))", file=sys.stderr)
                return 2
            rate = p / split_n if split_n > 0 else 0.0
            rates.append((name, rate, p, split_n))
            print(f"    {name:<5}: {p} positive / {split_n} = {rate:.4f}")
            if p < _MIN_MINORITY_COUNT:
                print(f"    WARNING: {name} has only {p} positive examples — too few to trust "
                      "the balance; the rare class may be effectively absent. Stratify the split.")
        if len(rates) >= 2:
            present = [r for _, r, _, _ in rates]
            lo, hi = min(present), max(present)
            base = hi if hi > 0 else 1.0
            if (hi - lo) / base > _BALANCE_DRIFT_REL:
                print(f"    WARNING: positive rate drifts from {lo:.4f} to {hi:.4f} across "
                      "splits — stratify on the target so each split has the same class balance.")
    print("  reminder: split BEFORE you touch the data — fit every transform inside the fold.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ds_calc.py",
        description="Data-science-research evaluation calculator (stdlib only, Python 3.8+). "
        "Decision-support, not a substitute for honest evaluation — cross-validate, "
        "report uncertainty, and confirm no leakage.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    cm = sub.add_parser(
        "classification-metrics",
        help="precision / recall / F1 / accuracy from a confusion matrix",
    )
    cm.add_argument("--tp", type=int, required=True, help="true positives")
    cm.add_argument("--fp", type=int, required=True, help="false positives")
    cm.add_argument("--fn", type=int, required=True, help="false negatives")
    cm.add_argument("--tn", type=int, required=True, help="true negatives")
    cm.set_defaults(func=cmd_classification_metrics)

    rm = sub.add_parser(
        "regression-metrics",
        help="MAE / RMSE / R2 from paired y_true / y_pred lists",
    )
    rm.add_argument("--y-true", dest="y_true", type=float, nargs="+", required=True,
                    help="actual values, space-separated")
    rm.add_argument("--y-pred", dest="y_pred", type=float, nargs="+", required=True,
                    help="predicted values, space-separated (same length as --y-true)")
    rm.set_defaults(func=cmd_regression_metrics)

    sc = sub.add_parser(
        "split-check",
        help="train / val / test ratio sanity + class-balance warning",
    )
    sc.add_argument("--train", type=float, required=True, help="train fraction (e.g. 0.7)")
    sc.add_argument("--val", type=float, required=True, help="validation fraction (e.g. 0.15)")
    sc.add_argument("--test", type=float, required=True, help="test fraction (e.g. 0.15)")
    sc.add_argument("--min-frac", dest="min_frac", type=float, default=0.10,
                    help="warn if any split is below this fraction (default 0.10)")
    sc.add_argument("--n", type=int, default=None,
                    help="total row count — required to check per-split class balance")
    sc.add_argument("--pos-train", dest="pos_train", type=int, default=None,
                    help="positive-class count in the train split")
    sc.add_argument("--pos-val", dest="pos_val", type=int, default=None,
                    help="positive-class count in the val split")
    sc.add_argument("--pos-test", dest="pos_test", type=int, default=None,
                    help="positive-class count in the test split")
    sc.set_defaults(func=cmd_split_check)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
