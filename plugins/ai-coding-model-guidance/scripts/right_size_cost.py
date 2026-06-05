#!/usr/bin/env python3
"""right_size_cost.py — a zero-dependency cost-per-resolved-task right-sizing helper.

The `ai-coding-model-guidance` agents keep asserting that the metric for model
selection is **cost-per-resolved-task, not model rank** — but the plugin shipped
no tool to actually compute it. This is that tool. It removes the arithmetic
error from two recurring right-sizing decisions across GitHub Copilot, OpenAI
Codex, and xAI Grok:

  per-task    Rank candidate tiers by COST-PER-RESOLVED-TASK. For each tier you
              supply its per-call cost and its first-try resolution rate (the
              fraction of tasks it gets right without a retry); the tool computes
              the expected cost to resolve ONE task including retries
              (cost-per-call / resolution-rate), ranks the tiers, and names the
              cheapest-per-resolved-task option. A pricier model that one-shots a
              hard task can win; a cheap model that needs many retries can lose —
              this surfaces which.

  mix         Split a day across task SHAPES (e.g. inline completion vs. a hard
              refactor) and compare a SINGLE-PIN strategy (one tier for the whole
              day) against a RIGHT-SIZED strategy (each shape gets its own tier).
              Prints the total cost of each strategy and the savings (or the
              premium) of right-sizing — the "I pinned the top model for
              everything" anti-pattern made numeric.

CRITICAL — NO PRICES ARE BAKED IN. This is a CALCULATOR, not a data source. It
does not know, fetch, or assume any vendor's price, context window, or model id.
EVERY number is user-supplied; the tool does the arithmetic and shows the
formula. The volatile facts live, dated and cited, in
../knowledge/cross-tool-model-lineup-2026.md — re-verify there (or at the live
vendor source) before feeding a number in. Pairs with the right-sizing decision
tree ../knowledge/ai-coding-right-size-cost-decision-tree.md.

Cost units are arbitrary and must be CONSISTENT within a run — premium requests,
dollars, tokens, credits: pick one and use it for every input. The tool reports
in whatever unit you fed it.

IMPORTANT: outputs are decision-support, not a price quote. Re-verify every
vendor number at use (CLAUDE.md §3 #4); the closed-world rule still applies to
any model id you reason about (CLAUDE.md §3 #5).

Examples
--------
  # Rank three tiers for the SAME task by cost-per-resolved-task.
  # Fast tier: 0.2/call, resolves 55% first try. Balanced: 1.0/call, 85%.
  # Frontier: 3.0/call, 96%.
  python3 right_size_cost.py per-task \\
      --tier fast:0.2:55% --tier balanced:1.0:85% --tier frontier:3.0:96%

  # Compare pinning ONE tier all day vs. right-sizing per shape.
  # 400 completions/day @ fast=0.2, balanced=1.0; 6 hard tasks/day @ same.
  # Single-pin uses 'balanced' for everything; right-sized uses fast for
  # completions and frontier (3.0) for the hard tasks.
  python3 right_size_cost.py mix \\
      --shape completion:400:0.2:1.0:3.0 \\
      --shape hard:6:0.2:1.0:3.0 \\
      --single-pin balanced
"""

from __future__ import annotations

import argparse
import sys


def _parse_pct(text: str) -> float:
    """Parse '85%' or '0.85' into a fraction in (0, 1]."""
    text = text.strip()
    if text.endswith("%"):
        value = float(text[:-1]) / 100.0
    else:
        value = float(text)
    if not 0.0 < value <= 1.0:
        raise ValueError(f"resolution rate must be in (0, 1] / (0%, 100%], got {text!r}")
    return value


def _parse_tier(spec: str) -> tuple[str, float, float]:
    """Parse 'name:cost_per_call:resolution_rate' (rate as 85% or 0.85)."""
    parts = spec.split(":")
    if len(parts) != 3:
        raise ValueError(
            f"--tier expects name:cost_per_call:resolution_rate, got {spec!r}"
        )
    name, cost_s, rate_s = parts
    cost = float(cost_s)
    if cost < 0:
        raise ValueError(f"cost-per-call cannot be negative, got {cost_s!r}")
    return name.strip(), cost, _parse_pct(rate_s)


def _parse_shape(spec: str) -> tuple[str, float, float, float, float]:
    """Parse 'name:count:fast_cost:balanced_cost:frontier_cost' per-call costs."""
    parts = spec.split(":")
    if len(parts) != 5:
        raise ValueError(
            "--shape expects name:count:fast_cost:balanced_cost:frontier_cost, "
            f"got {spec!r}"
        )
    name, count_s, fast_s, bal_s, front_s = parts
    count = float(count_s)
    if count < 0:
        raise ValueError(f"count cannot be negative, got {count_s!r}")
    costs = [float(fast_s), float(bal_s), float(front_s)]
    if any(c < 0 for c in costs):
        raise ValueError(f"costs cannot be negative in {spec!r}")
    return name.strip(), count, costs[0], costs[1], costs[2]


def cmd_per_task(args: argparse.Namespace) -> int:
    tiers = [_parse_tier(s) for s in args.tier]
    if not tiers:
        print("error: supply at least one --tier", file=sys.stderr)
        return 2

    print("Cost-per-RESOLVED-task ranking")
    print("(expected cost to resolve one task = cost-per-call / resolution-rate)\n")
    rows = []
    for name, cost, rate in tiers:
        per_resolved = cost / rate
        rows.append((per_resolved, name, cost, rate))
        print(
            f"  {name:<12} {cost:>10.4g}/call  x  1/{rate:.0%} resolve  "
            f"=  {per_resolved:>10.4g} per resolved task"
        )

    rows.sort(key=lambda r: r[0])
    best_cost, best_name = rows[0][0], rows[0][1]
    print(f"\nRight-sized (cheapest per RESOLVED task): {best_name} "
          f"({best_cost:.4g}/resolved task)")
    if len(rows) > 1:
        runner = rows[1]
        delta = (runner[0] - best_cost) / best_cost * 100 if best_cost else 0.0
        print(
            f"Next best: {runner[1]} at {runner[0]:.4g} "
            f"(+{delta:.0f}% per resolved task)"
        )
    print(
        "\nNote: rank by cost-per-RESOLVED-task, not model rank. Re-verify every "
        "cost figure at use against ../knowledge/cross-tool-model-lineup-2026.md."
    )
    return 0


def cmd_mix(args: argparse.Namespace) -> int:
    shapes = [_parse_shape(s) for s in args.shape]
    if not shapes:
        print("error: supply at least one --shape", file=sys.stderr)
        return 2

    pin_index = {"fast": 0, "balanced": 1, "frontier": 2}.get(args.single_pin)
    if pin_index is None:
        print(
            f"error: --single-pin must be fast|balanced|frontier, "
            f"got {args.single_pin!r}",
            file=sys.stderr,
        )
        return 2

    print(f"Single-pin ({args.single_pin}) vs. right-sized per shape\n")
    single_total = 0.0
    right_total = 0.0
    tier_names = ("fast", "balanced", "frontier")
    for name, count, fast_c, bal_c, front_c in shapes:
        costs = (fast_c, bal_c, front_c)
        single_cost = count * costs[pin_index]
        best_idx = min(range(3), key=lambda i: costs[i])
        right_cost = count * costs[best_idx]
        single_total += single_cost
        right_total += right_cost
        print(
            f"  {name:<12} count={count:<8g}  "
            f"single-pin({args.single_pin})={single_cost:>10.4g}  "
            f"right-sized({tier_names[best_idx]})={right_cost:>10.4g}"
        )

    saved = single_total - right_total
    print(f"\n  {'TOTAL':<12} single-pin={single_total:>10.4g}  "
          f"right-sized={right_total:>10.4g}")
    if single_total > 0:
        pct = saved / single_total * 100
        if saved > 0:
            print(f"\nRight-sizing saves {saved:.4g} ({pct:.0f}% of the single-pin bill).")
        elif saved < 0:
            print(f"\nSingle-pin is already cheapest here (right-sizing would add "
                  f"{-saved:.4g}). Verify your per-shape costs.")
        else:
            print("\nNo difference — the single pin is already the cheapest tier "
                  "for every shape.")
    print(
        "\nNote: 'right-sized' picks the cheapest tier per shape by the COSTS YOU "
        "SUPPLIED (it does not score quality — feed costs only for tiers that "
        "actually RESOLVE that shape). Re-verify costs at use; no prices are baked in."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="right_size_cost.py",
        description="Cost-per-resolved-task right-sizing helper (NO baked-in prices).",
    )
    sub = p.add_subparsers(dest="command", required=True)

    pt = sub.add_parser(
        "per-task",
        help="Rank candidate tiers by cost-per-resolved-task for ONE task.",
    )
    pt.add_argument(
        "--tier",
        action="append",
        default=[],
        metavar="name:cost_per_call:resolution_rate",
        help="A candidate tier, e.g. balanced:1.0:85% (rate as 85% or 0.85). Repeatable.",
    )
    pt.set_defaults(func=cmd_per_task)

    mx = sub.add_parser(
        "mix",
        help="Compare single-pin vs. right-sized across task shapes.",
    )
    mx.add_argument(
        "--shape",
        action="append",
        default=[],
        metavar="name:count:fast_cost:balanced_cost:frontier_cost",
        help="A task shape's per-day count and per-call cost at each tier. Repeatable.",
    )
    mx.add_argument(
        "--single-pin",
        required=True,
        choices=("fast", "balanced", "frontier"),
        help="Which single tier the 'pin one model for everything' strategy uses.",
    )
    mx.set_defaults(func=cmd_mix)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (ValueError, ZeroDivisionError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
