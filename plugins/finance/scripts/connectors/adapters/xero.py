#!/usr/bin/env python3
"""Xero adapter. Emits a RAW export with SEPARATE Debit/Credit columns (Xero header names).
Reference-impl / offline; tb_stage.py normalizes via fixtures/xero/column-map.json.
Not a live connector (../../../CLAUDE.md sec.3)."""
from __future__ import annotations

from ._base import split_debit_credit, write_raw

PROVIDER = "xero"
FIXTURE = "xero/trial_balance"
COLUMN_MAP = "xero/column-map.json"
HEADER = ["AccountID", "AccountName", "Debit", "Credit"]


def export(transport, out_path: str) -> str:
    payload = transport.fetch(FIXTURE)
    rows = []
    for r in payload["rows"]:
        debit, credit = split_debit_credit(r["amount"])
        rows.append([r["account"], r["name"], debit, credit])
    return write_raw(out_path, HEADER, rows)
