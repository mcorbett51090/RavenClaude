#!/usr/bin/env python3
"""recon_diff.py — a zero-dependency ledger-vs-PSP reconciliation differ.

Mechanizes the Reconciliation-discrepancy-triage decision tree
(../knowledge/fintech-payments-engineering-decision-trees.md): take your
internal double-entry ledger's view of money movements and the PSP's report of
the same window, match them by a shared transaction reference, and classify
every non-zero difference into the tree's buckets so each gets an owner instead
of being written off.

It answers the three questions the tree branches on, per reference:

  PSP_ONLY        The PSP has a charge your ledger is missing.
                  -> likely a dropped/unprocessed webhook; replay it, post the entry.
  LEDGER_ONLY     Your ledger has an entry with no PSP counterpart.
                  -> phantom credit / double-post; investigate idempotency + dedupe.
  AMOUNT_MISMATCH A matched pair whose amounts differ.
                  -> explained by fees/FX/partial capture (model it) OR an
                     unexplained money delta (escalate: bug or fraud).
  MATCHED         Amounts agree (optionally after subtracting known PSP fees).

Money is handled as INTEGER MINOR UNITS (cents) end to end — never floats
(CLAUDE.md §2 #1). A row whose amount is not an integer is rejected loudly
rather than silently coerced. Matching is exact on (reference, currency); a
currency mismatch on a shared reference is itself flagged, never netted.

This is a DIFFER, not a money-mover: it reads two files and prints a triage
report + a machine-readable JSON summary. It posts nothing, calls no PSP, and
makes no network request. Stdlib only (argparse, csv, json); Python 3.9+.

IMPORTANT: output is engineering decision-support. The accounting treatment of
any delta (revenue recognition, GL) routes to `finance`; a suspected-fraud or
breach delta routes to `ravenclaude-core/security-reviewer` (CLAUDE.md §3).

Input format
------------
Two CSV files, each with a header row. Required columns (extra columns ignored):

  reference   shared transaction id present in both sides (e.g. PSP charge id)
  amount      integer minor units (cents); refunds/reversals are negative
  currency    ISO 4217 code (e.g. usd); compared case-insensitively

The PSP file MAY carry a `fee` column (integer minor units) — when --net-fees
is passed, the PSP amount is compared net of fee so a matched pair isn't
reported as a mismatch purely because the PSP withheld its fee.

Examples
--------
  # Straight diff
  python3 recon_diff.py --ledger ledger.csv --psp psp.csv

  # Treat differences within the PSP 'fee' column as explained
  python3 recon_diff.py --ledger ledger.csv --psp psp.csv --net-fees

  # Machine-readable summary only (for a CI recon gate)
  python3 recon_diff.py --ledger ledger.csv --psp psp.csv --json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys


class ReconError(Exception):
    """A fatal input problem — surfaced loudly, never silently coerced."""


def _parse_int_minor(value: str, *, row: int, col: str, path: str) -> int:
    """Parse an integer minor-unit amount; reject floats/garbage loudly."""
    raw = (value or "").strip()
    if raw == "":
        raise ReconError(f"{path} row {row}: empty '{col}' (need integer minor units)")
    try:
        # int(str) rejects "12.50" and "abc" — exactly what we want: money is
        # integer cents, a decimal point here means the source is using floats.
        return int(raw)
    except ValueError as exc:
        raise ReconError(
            f"{path} row {row}: '{col}'={raw!r} is not integer minor units "
            f"(money must be integer cents, never a float) — {exc}"
        ) from None


def _load(path: str, *, want_fee: bool) -> dict[tuple[str, str], dict]:
    """Load a side into {(reference, currency_lower): {...}}.

    A duplicate (reference, currency) within one file is itself a defect
    (a double-post on the ledger side, a duplicate report row on the PSP
    side) and is reported rather than silently overwritten.
    """
    rows: dict[tuple[str, str], dict] = {}
    try:
        with open(path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ReconError(f"{path}: empty file (no header row)")
            missing = {"reference", "amount", "currency"} - set(reader.fieldnames)
            if missing:
                raise ReconError(
                    f"{path}: missing required column(s): {', '.join(sorted(missing))}"
                )
            for i, raw in enumerate(reader, start=2):  # row 1 is the header
                ref = (raw.get("reference") or "").strip()
                if ref == "":
                    raise ReconError(f"{path} row {i}: empty 'reference'")
                currency = (raw.get("currency") or "").strip().lower()
                if currency == "":
                    raise ReconError(f"{path} row {i}: empty 'currency'")
                amount = _parse_int_minor(raw["amount"], row=i, col="amount", path=path)
                fee = 0
                if want_fee and raw.get("fee", "").strip() != "":
                    fee = _parse_int_minor(raw["fee"], row=i, col="fee", path=path)
                key = (ref, currency)
                if key in rows:
                    raise ReconError(
                        f"{path} row {i}: duplicate (reference={ref}, currency={currency}) "
                        f"— a duplicate row is itself a recon defect; resolve it before diffing"
                    )
                rows[key] = {"reference": ref, "currency": currency, "amount": amount, "fee": fee}
    except FileNotFoundError:
        raise ReconError(f"{path}: file not found") from None
    return rows


def reconcile(
    ledger: dict[tuple[str, str], dict],
    psp: dict[tuple[str, str], dict],
    *,
    net_fees: bool,
) -> dict:
    """Classify every reference into the triage buckets. Pure; no I/O."""
    psp_only: list[dict] = []
    ledger_only: list[dict] = []
    amount_mismatch: list[dict] = []
    matched = 0

    # Cross-currency check on shared references: a reference present on both
    # sides but under different currencies is flagged, never netted.
    ledger_refs = {ref for (ref, _cur) in ledger}
    psp_refs = {ref for (ref, _cur) in psp}
    currency_mismatch: list[dict] = []
    for ref in ledger_refs & psp_refs:
        lcur = {c for (r, c) in ledger if r == ref}
        pcur = {c for (r, c) in psp if r == ref}
        if lcur != pcur:
            currency_mismatch.append(
                {"reference": ref, "ledger_currency": sorted(lcur), "psp_currency": sorted(pcur)}
            )

    for key, l_row in ledger.items():
        p_row = psp.get(key)
        if p_row is None:
            ledger_only.append(l_row)
            continue
        psp_amount = p_row["amount"] - (p_row["fee"] if net_fees else 0)
        if psp_amount == l_row["amount"]:
            matched += 1
        else:
            amount_mismatch.append(
                {
                    "reference": l_row["reference"],
                    "currency": l_row["currency"],
                    "ledger_amount": l_row["amount"],
                    "psp_amount": p_row["amount"],
                    "psp_fee": p_row["fee"],
                    "psp_amount_net_of_fee": psp_amount,
                    "delta": l_row["amount"] - psp_amount,
                }
            )

    for key, p_row in psp.items():
        if key not in ledger:
            psp_only.append(p_row)

    return {
        "matched": matched,
        "psp_only": psp_only,
        "ledger_only": ledger_only,
        "amount_mismatch": amount_mismatch,
        "currency_mismatch": currency_mismatch,
        "balanced": not (psp_only or ledger_only or amount_mismatch or currency_mismatch),
    }


def _print_report(result: dict, *, net_fees: bool) -> None:
    """Human-readable triage report keyed to the decision-tree buckets."""
    out = sys.stdout
    out.write("Ledger-vs-PSP reconciliation\n")
    out.write("=" * 60 + "\n")
    out.write(f"  matched:          {result['matched']}\n")
    out.write(f"  net of PSP fees:  {'yes' if net_fees else 'no'}\n\n")

    if result["balanced"]:
        out.write("BALANCED — every reference matched. No triage needed.\n")
        return

    if result["psp_only"]:
        out.write(f"PSP_ONLY ({len(result['psp_only'])}) — PSP has a charge the ledger is missing.\n")
        out.write("  Tree: likely a dropped/unprocessed webhook — replay it, post the entry.\n")
        for r in result["psp_only"]:
            out.write(f"    - {r['reference']}  {r['amount']} {r['currency']}\n")
        out.write("\n")

    if result["ledger_only"]:
        out.write(f"LEDGER_ONLY ({len(result['ledger_only'])}) — ledger entry with no PSP counterpart.\n")
        out.write("  Tree: phantom credit / double-post — investigate idempotency + dedupe.\n")
        for r in result["ledger_only"]:
            out.write(f"    - {r['reference']}  {r['amount']} {r['currency']}\n")
        out.write("\n")

    if result["amount_mismatch"]:
        out.write(f"AMOUNT_MISMATCH ({len(result['amount_mismatch'])}) — matched pair, amounts differ.\n")
        out.write("  Tree: explained by fees/FX/partial capture? Model it and re-match.\n")
        out.write("        Unexplained delta = bug or fraud -> escalate (security-reviewer).\n")
        for r in result["amount_mismatch"]:
            out.write(
                f"    - {r['reference']} {r['currency']}: ledger={r['ledger_amount']} "
                f"psp={r['psp_amount']} (net={r['psp_amount_net_of_fee']}, "
                f"fee={r['psp_fee']}) delta={r['delta']}\n"
            )
        out.write("\n")

    if result["currency_mismatch"]:
        out.write(
            f"CURRENCY_MISMATCH ({len(result['currency_mismatch'])}) — shared reference, "
            f"different currency. Never net these.\n"
        )
        for r in result["currency_mismatch"]:
            out.write(
                f"    - {r['reference']}: ledger={r['ledger_currency']} psp={r['psp_currency']}\n"
            )
        out.write("\n")

    out.write("A non-zero difference is a defect with an owner until proven otherwise.\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="recon_diff.py",
        description="Diff an internal ledger against a PSP report; triage every discrepancy.",
    )
    parser.add_argument("--ledger", required=True, help="CSV of your ledger view (reference, amount, currency)")
    parser.add_argument("--psp", required=True, help="CSV of the PSP report (reference, amount, currency[, fee])")
    parser.add_argument(
        "--net-fees",
        action="store_true",
        help="Compare PSP amounts net of the PSP 'fee' column (fees are an explained delta)",
    )
    parser.add_argument("--json", action="store_true", help="Emit only the machine-readable JSON summary")
    args = parser.parse_args(argv)

    try:
        ledger = _load(args.ledger, want_fee=False)
        psp = _load(args.psp, want_fee=args.net_fees)
    except ReconError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 2

    result = reconcile(ledger, psp, net_fees=args.net_fees)

    if args.json:
        sys.stdout.write(json.dumps(result, indent=2) + "\n")
    else:
        _print_report(result, net_fees=args.net_fees)

    # Exit 1 on any discrepancy so a CI recon gate can fail the build.
    return 0 if result["balanced"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
