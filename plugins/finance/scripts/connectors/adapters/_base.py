"""Shared adapter helpers. Reference-impl / offline; not a live connector."""
from __future__ import annotations

import csv


def split_debit_credit(amount: float) -> tuple:
    """Split a signed (debit-positive) net amount into (debit, credit) display strings.
    A non-negative amount is a debit; a negative amount is a credit (its absolute value)."""
    amount = float(amount)
    if amount >= 0:
        return (_fmt(amount), "0")
    return ("0", _fmt(-amount))


def _fmt(n: float) -> str:
    n = round(n + 0.0, 2)
    return str(int(n)) if n == int(n) else f"{n:.2f}"


def signed(amount: float) -> str:
    """Signed net amount as a display string (for single-amount-column vendors)."""
    return _fmt(float(amount))


def write_raw(out_path: str, header: list, rows: list) -> str:
    """Write a raw vendor export CSV (\\n line endings). Returns out_path."""
    with open(out_path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    return out_path
