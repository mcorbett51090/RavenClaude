#!/usr/bin/env python3
"""QuickBooks Online adapter. Emits a RAW export with SEPARATE Debit/Credit columns
(the QBO TrialBalance report shape). Reference-impl / offline; tb_stage.py normalizes the
output via fixtures/qbo/column-map.json. Not a live connector (../../../CLAUDE.md sec.3)."""
from __future__ import annotations

from ._base import split_debit_credit, write_raw

PROVIDER = "qbo"
FIXTURE = "qbo/trial_balance"
COLUMN_MAP = "qbo/column-map.json"
HEADER = ["Account #", "Account Name", "Debit", "Credit"]


def export(transport, out_path: str) -> str:
    payload = transport.fetch(FIXTURE)
    rows = []
    for r in payload["rows"]:
        debit, credit = split_debit_credit(r["amount"])
        rows.append([r["account"], r["name"], debit, credit])
    return write_raw(out_path, HEADER, rows)
