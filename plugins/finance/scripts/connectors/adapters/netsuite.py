#!/usr/bin/env python3
"""NetSuite adapter. Emits a RAW export with ONE signed net-amount column (SuiteQL result
shape). Reference-impl / offline; tb_stage.py normalizes via fixtures/netsuite/column-map.json
(amount_column split). Not a live connector (../../../CLAUDE.md sec.3)."""
from __future__ import annotations

from ._base import signed, write_raw

PROVIDER = "netsuite"
FIXTURE = "netsuite/trial_balance"
COLUMN_MAP = "netsuite/column-map.json"
HEADER = ["Account", "Memo", "Net Amount (Signed)"]


def export(transport, out_path: str) -> str:
    payload = transport.fetch(FIXTURE)
    rows = [[r["account"], r["name"], signed(r["amount"])] for r in payload["rows"]]
    return write_raw(out_path, HEADER, rows)
