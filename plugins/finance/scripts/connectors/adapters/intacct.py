#!/usr/bin/env python3
"""Sage Intacct adapter. Emits a RAW export with SEPARATE DEBIT/CREDIT columns (Intacct
readByQuery header names). Reference-impl / offline; tb_stage.py normalizes via
fixtures/intacct/column-map.json. Not a live connector (../../../CLAUDE.md sec.3)."""
from __future__ import annotations

from ._base import split_debit_credit, write_raw

PROVIDER = "intacct"
FIXTURE = "intacct/trial_balance"
COLUMN_MAP = "intacct/column-map.json"
HEADER = ["ACCOUNTNO", "TITLE", "DEBIT", "CREDIT"]


def export(transport, out_path: str) -> str:
    payload = transport.fetch(FIXTURE)
    rows = []
    for r in payload["rows"]:
        debit, credit = split_debit_credit(r["amount"])
        rows.append([r["account"], r["name"], debit, credit])
    return write_raw(out_path, HEADER, rows)
