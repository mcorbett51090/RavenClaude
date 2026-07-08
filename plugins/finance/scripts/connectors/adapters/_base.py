"""Shared adapter helpers. Reference-impl / offline; not a live connector."""

from __future__ import annotations

import csv
from decimal import ROUND_HALF_UP, Decimal


def _to_decimal(amount) -> Decimal:
    """Coerce str/Decimal/int/float to Decimal at the money boundary.
    str/Decimal/int preserve their exact value; a float is stringified first so the
    binary approximation (2.675 -> 2.67499...) does not leak into the Decimal."""
    if isinstance(amount, Decimal):
        return amount
    if isinstance(amount, float):
        return Decimal(str(amount))
    return Decimal(amount)


def split_debit_credit(amount) -> tuple:
    """Split a signed (debit-positive) net amount into (debit, credit) display strings.
    A non-negative amount is a debit; a negative amount is a credit (its absolute value).
    Accepts str/Decimal/int/float; money is quantized via Decimal (half-up)."""
    amount = _to_decimal(amount)
    if amount >= 0:
        return (_fmt(amount), "0")
    return ("0", _fmt(-amount))


def _fmt(n) -> str:
    """Format a money amount to an exact, half-up 2-decimal string, dropping the
    decimals when the value is integral (e.g. 5 -> "5", 2.675 -> "2.68")."""
    q = _to_decimal(n).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return str(int(q)) if q == q.to_integral_value() else f"{q:.2f}"


def signed(amount) -> str:
    """Signed net amount as a display string (for single-amount-column vendors)."""
    return _fmt(_to_decimal(amount))


def write_raw(out_path: str, header: list, rows: list) -> str:
    """Write a raw vendor export CSV (\\n line endings). Returns out_path."""
    with open(out_path, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)
    return out_path
