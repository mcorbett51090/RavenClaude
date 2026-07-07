#!/usr/bin/env python3
"""NetSuite adapter. Emits a RAW export with ONE signed net-amount column (SuiteQL result
shape). Reference-impl / offline; tb_stage.py normalizes via fixtures/netsuite/column-map.json
(amount_column split). Not a live connector (../../../CLAUDE.md sec.3)."""
from __future__ import annotations

import os
import sys

from ._base import signed, write_raw

_CONN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _CONN not in sys.path:
    sys.path.insert(0, _CONN)

PROVIDER = "netsuite"
FIXTURE = "netsuite/trial_balance"
COLUMN_MAP = "netsuite/column-map.json"
HEADER = ["Account", "Memo", "Net Amount (Signed)"]


def export(transport, out_path: str) -> str:
    payload = transport.fetch(FIXTURE)
    rows = [[r["account"], r["name"], signed(r["amount"])] for r in payload["rows"]]
    return write_raw(out_path, HEADER, rows)


def export_via_suiteql(transport, period_id, out_path: str, *, subsidiary=None,
                       book=None) -> str:
    """The GOLD-STANDARD path: build the BS-cumulative / IS-period SuiteQL TB query, page it
    serially under the governance cap, TIE OUT (net-to-zero) BEFORE staging, then emit the
    same raw-export shape tb_stage.py + netsuite/column-map.json already normalize UNCHANGED.
    A non-tying pull raises loudly rather than staging a broken TB."""
    import suiteql  # local import: keeps the thin `export` path dependency-free

    query = suiteql.build_tb_query(period_id, subsidiary=subsidiary, book=book)
    rows = suiteql.pull(transport, query)
    suiteql.tie_out(rows)
    out_rows = [[r["account"], r["name"], signed(r["amount"])] for r in rows]
    return write_raw(out_path, HEADER, out_rows)
