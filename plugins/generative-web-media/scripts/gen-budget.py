#!/usr/bin/env python3
"""gen-budget.py — a per-project generation-spend ledger + budget guard.

Cost control is a rubric ★ row: route a cheap draft before a premium final, and cap
per-project generation spend so it is a design input, not a surprise. This tool logs
spend lines and reports spend-vs-budget, failing LOUDLY when the cap is exceeded.

IT BAKES IN ZERO PRICES. Every unit price is a USER INPUT — provider prices are
date/plan-volatile and marked [unverified] in the matrix; pull the live number from
the provider's pricing page and pass it in. Outputs are decision-support arithmetic,
not a quote.

Stdlib only. PROBE-AND-DEGRADE: bad input fails LOUDLY (non-zero), never a silent
pass. Ledger format is JSON Lines.

Usage:
  gen-budget.py add --ledger media/spend.jsonl --model flux2-pro \\
      --unit-price 0.055 --count 8 [--tier draft|final] [--label "hero variants"]
  gen-budget.py status --ledger media/spend.jsonl --budget 25.00
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _loud_fail(message: str) -> int:
    sys.stderr.write(f"\n[gen-budget] FAIL — THIS IS NOT A PASS.\n{message}\n\n")
    return 1


def cmd_add(args: argparse.Namespace) -> int:
    if args.unit_price < 0 or args.count < 0:
        return _loud_fail("--unit-price and --count must be non-negative.")
    line_cost = round(args.unit_price * args.count, 6)
    entry = {
        "recorded_at": _now_iso(),
        "model": args.model,
        "tier": args.tier,
        "unit_price": args.unit_price,
        "count": args.count,
        "line_cost": line_cost,
        "label": args.label,
        "price_source": "user-supplied [unverified — confirm on provider pricing page]",
    }
    ledger = Path(args.ledger)
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    sys.stdout.write(json.dumps({"ok": True, "line_cost": line_cost, "ledger": str(ledger)}) + "\n")
    return 0


def _read_lines(path: Path) -> list[dict]:
    out: list[dict] = []
    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{i}: not valid JSON ({exc.msg})") from exc
        if not isinstance(obj, dict):
            raise ValueError(f"{path}:{i}: line is valid JSON but not an object")
        out.append(obj)
    return out


def cmd_status(args: argparse.Namespace) -> int:
    ledger = Path(args.ledger)
    if not ledger.is_file():
        return _loud_fail(f"Ledger not found: {ledger}")
    try:
        entries = _read_lines(ledger)
    except ValueError as exc:
        return _loud_fail(str(exc))

    spent = round(sum(float(e.get("line_cost", 0.0)) for e in entries), 6)
    by_tier: dict[str, float] = {}
    for e in entries:
        by_tier[e.get("tier", "unspecified")] = round(
            by_tier.get(e.get("tier", "unspecified"), 0.0) + float(e.get("line_cost", 0.0)), 6
        )
    remaining = round(args.budget - spent, 6)
    over = spent > args.budget

    report = {
        "ledger": str(ledger),
        "lines": len(entries),
        "budget": args.budget,
        "spent": spent,
        "remaining": remaining,
        "by_tier": by_tier,
        "over_budget": over,
        "note": "prices are user-supplied [unverified — confirm on provider pricing page]",
    }
    sys.stdout.write(json.dumps(report, indent=2) + "\n")
    if over:
        return _loud_fail(
            f"OVER BUDGET: spent {spent} > budget {args.budget} (over by {round(spent - args.budget, 6)}). "
            "Stop generating, or raise the cap deliberately."
        )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="append a spend line (you supply the unit price)")
    add.add_argument("--ledger", required=True)
    add.add_argument("--model", required=True)
    add.add_argument("--unit-price", dest="unit_price", type=float, required=True)
    add.add_argument("--count", type=int, required=True)
    add.add_argument("--tier", default="unspecified", help="draft | final | unspecified")
    add.add_argument("--label", default="")
    add.set_defaults(func=cmd_add)

    st = sub.add_parser("status", help="report spend vs budget (fails if over)")
    st.add_argument("--ledger", required=True)
    st.add_argument(
        "--budget", type=float, required=True, help="the per-project cap, in your currency"
    )
    st.set_defaults(func=cmd_status)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
