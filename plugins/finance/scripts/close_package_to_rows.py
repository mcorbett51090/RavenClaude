#!/usr/bin/env python3
"""close_package_to_rows.py - flatten a governed close package into warehouse rows.

WHAT THIS IS (and is NOT). This is the finance-specific *delta* between the single-
entity, file-in/file-out close package (`controller_cycle.py --out-json`) and a
recurring, warehouse-backed, MULTI-TENANT dashboard. It loads ONE close package and
emits the dimensional fact/dim rows a controller's portfolio dashboard reads:

    dim_entity            one row per legal entity (the tenant axis)
    dim_period            one row per fiscal period (YYYY-MM + day count)
    fct_close_statement_line   IS/BS lines (section x line), presentation-signed
    fct_recon_exception   reconciliation tie-out rows (PASS / FLAG / self-supported)
    fct_flux_movement     materiality-suppressed period-over-period movements
    fct_close_kpi          the headline KPIs — ported VERBATIM from entity_dashboard
    fct_close_state       the governed close state + traceability / self-cert badges

Grain is entity_id x period. It RECOMPUTES no statement math: every line, badge, and
materiality suppression flows through from the committed package unchanged. The KPI
fact is produced by *importing and calling* `entity_dashboard.derive_kpis` — not a
re-implementation — so the warehouse KPIs are byte-for-byte the same values the
single-entity dashboard shows (KPI parity), and an input the package lacks lands as
`value = null / is_na = true`, never a plugged number.

WHAT THIS IS NOT. It does not connect to a warehouse, load anything, issue a token,
or enforce a tenant boundary. That is `entity_rls.py` (the array-claim resolver) plus
the reference dbt/Cube/Postgres-RLS artifacts under
`skills/warehouse-dashboard/models/` — SQL/YAML that is *specified, not executed*
here (there is no warehouse in this repo). The security surface REUSES data-platform
(`rls-policy-authoring`, `jwt-embed-issuance`, `cube-schema-scaffolding`,
`dbt-project-scaffolding`); it is not hand-rolled.

Outputs are decision-support / a reference implementation, NOT an audited close or a
live-verified pipeline. Live wiring, an IdP, a warehouse, and real credentials are
the consumer's step, gated through `ravenclaude-core/security-reviewer`
(../CLAUDE.md sec.3, sec.10). Stdlib only (csv/json/argparse/hashlib/os/sys).
Python 3.8+.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import entity_dashboard as ed  # noqa: E402  (derive_kpis is the KPI source of truth)

# Fixed namespace so the SAME entity name always derives the SAME surrogate id.
# This is a deterministic surrogate KEY, not a cryptographic function — sha256 is
# used only to spread names uniformly across the id space (no security property is
# claimed of it). A consumer with a real warehouse entity id passes --entity-id.
_ID_NAMESPACE = b"ravenclaude.finance.warehouse-dashboard.v1"

# Tables that carry the entity axis (used by the RLS/Cube reference to know what to
# scope). dim_period is intentionally NOT here — a fiscal period is not tenant-secret.
ENTITY_SCOPED_TABLES = (
    "dim_entity",
    "fct_close_statement_line",
    "fct_recon_exception",
    "fct_flux_movement",
    "fct_close_kpi",
    "fct_close_state",
)


def entity_uuid(name: str) -> str:
    """Deterministic UUID-shaped surrogate id for an entity name (stdlib only).

    Mirrors the *shape* of a RFC-4122 v-style UUID (version/variant bits set) so it
    slots into a `uuid` column and the `entity_id = ANY(...::uuid[])` RLS predicate,
    without importing `uuid`. Same name in -> same id out (stable across runs).
    """
    digest = hashlib.sha256(_ID_NAMESPACE + name.encode("utf-8")).digest()
    b = bytearray(digest[:16])
    b[6] = (b[6] & 0x0F) | 0x50  # version nibble (5-style: name-based)
    b[8] = (b[8] & 0x3F) | 0x80  # RFC-4122 variant
    h = b.hex()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def _split_period(period: str):
    """('YYYY-MM') -> (year, month) ints, else (None, None)."""
    try:
        y, m = str(period).split("-")[:2]
        yi, mi = int(y), int(m)
        return (yi, mi) if 1 <= mi <= 12 else (None, None)
    except (ValueError, IndexError):
        return None, None


def to_rows(pkg: dict, entity_id: str | None = None) -> dict:
    """Flatten a close package into {table_name: [row, ...]}. No math is recomputed."""
    name = str(pkg.get("entity", ""))
    period = str(pkg.get("period", ""))
    currency = str(pkg.get("currency", ""))
    eid = entity_id or entity_uuid(name)
    st = pkg.get("statements") or {}

    dim_entity = [{
        "entity_id": eid,
        "entity_name": name,
        "functional_currency": currency,
    }]

    days = ed._days_in_period(period)
    year, month = _split_period(period)
    dim_period = [{
        "period_id": period,
        "fiscal_year": year,
        "fiscal_month": month,
        "day_count": days,
    }]

    # fct_close_statement_line — aggregate the reasoning trail to (statement, section,
    # line) grain, summing the ALREADY presentation-signed amounts (contra-safe: the
    # engine signed them by section, we only add). No re-signing here.
    trail = st.get("reasoning_trail") or {}
    agg: dict = {}
    for tkey, code in (("income_statement", "IS"), ("balance_sheet", "BS")):
        for e in trail.get(tkey) or []:
            key = (code, str(e.get("section", "")), str(e.get("line", "")))
            agg[key] = round(agg.get(key, 0.0) + float(e.get("amount") or 0.0), 2)
    fct_close_statement_line = [
        {"entity_id": eid, "period_id": period, "statement": s,
         "section": sec, "line": line, "amount": amt}
        for (s, sec, line), amt in sorted(agg.items())
    ]

    recon = pkg.get("reconciliation") or {}
    mat = recon.get("materiality_threshold")
    fct_recon_exception = [
        {"entity_id": eid, "period_id": period,
         "account": r.get("account"), "description": r.get("description"),
         "book_balance": r.get("book_balance"),
         "subledger_balance": r.get("subledger_balance"),
         "difference": r.get("difference"), "status": r.get("status"),
         "materiality_threshold": mat}
        for r in recon.get("accounts") or []
    ]

    flux = pkg.get("flux") or {}
    fct_flux_movement = [
        {"entity_id": eid, "period_id": period,
         "account": m.get("account"), "description": m.get("description"),
         "current": m.get("current"), "prior": m.get("prior"),
         "movement": m.get("movement"), "pct_change": m.get("pct_change")}
        for m in flux.get("material_movements") or []
    ]

    # fct_close_kpi — KPI PARITY by construction: the values are exactly what
    # entity_dashboard.derive_kpis returns for this package. A missing input is
    # carried as value=null / is_na=true (never plugged), same as the dashboard's n/a.
    kpi = ed.derive_kpis(pkg)
    fct_close_kpi = [
        {"entity_id": eid, "period_id": period, "metric": k,
         "value": v, "is_na": v is None}
        for k, v in kpi.items()
    ]

    ws = pkg.get("workflow_state") or {}
    fct_close_state = [{
        "entity_id": eid, "period_id": period,
        "state": ws.get("state"),
        "preparer": ws.get("preparer"),
        "self_certified": ws.get("self_certified"),
        "package_amount": ws.get("package_amount", pkg.get("package_amount")),
        "sod_threshold": pkg.get("sod_threshold"),
        "traceability_badge": st.get("traceability_badge"),
    }]

    return {
        "dim_entity": dim_entity,
        "dim_period": dim_period,
        "fct_close_statement_line": fct_close_statement_line,
        "fct_recon_exception": fct_recon_exception,
        "fct_flux_movement": fct_flux_movement,
        "fct_close_kpi": fct_close_kpi,
        "fct_close_state": fct_close_state,
    }


def _fieldnames(rows: list) -> list:
    """Stable column order = first row's key order (all rows share a schema)."""
    return list(rows[0].keys()) if rows else []


def write_csvs(tables: dict, out_dir: str) -> list:
    """Write one CSV per table (empty table -> header-only file). Returns paths."""
    os.makedirs(out_dir, exist_ok=True)
    written = []
    # A header even for empty tables keeps the warehouse-load contract stable.
    empty_headers = {
        "dim_entity": ["entity_id", "entity_name", "functional_currency"],
        "dim_period": ["period_id", "fiscal_year", "fiscal_month", "day_count"],
        "fct_close_statement_line": ["entity_id", "period_id", "statement",
                                     "section", "line", "amount"],
        "fct_recon_exception": ["entity_id", "period_id", "account", "description",
                                "book_balance", "subledger_balance", "difference",
                                "status", "materiality_threshold"],
        "fct_flux_movement": ["entity_id", "period_id", "account", "description",
                              "current", "prior", "movement", "pct_change"],
        "fct_close_kpi": ["entity_id", "period_id", "metric", "value", "is_na"],
        "fct_close_state": ["entity_id", "period_id", "state", "preparer",
                            "self_certified", "package_amount", "sod_threshold",
                            "traceability_badge"],
    }
    for table, rows in tables.items():
        path = os.path.join(out_dir, table + ".csv")
        fields = _fieldnames(rows) or empty_headers.get(table, [])
        with open(path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        written.append(path)
    return written


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Flatten a close-package JSON into warehouse fact/dim rows.")
    p.add_argument("--package", required=True,
                   help="close-package JSON (controller_cycle.py --out-json shape)")
    p.add_argument("--entity-id",
                   help="explicit warehouse entity_id (UUID); default derived from name")
    p.add_argument("--out-json", help="write the full {table: rows} JSON here")
    p.add_argument("--out-dir", help="write one CSV per table into this directory")
    a = p.parse_args(argv)

    with open(a.package) as fh:
        pkg = json.load(fh)
    tables = to_rows(pkg, a.entity_id)

    if a.out_dir:
        paths = write_csvs(tables, a.out_dir)
        counts = {t: len(r) for t, r in tables.items()}
        print(f"wrote {len(paths)} CSV(s) to {a.out_dir}  "
              f"[entity_id {tables['dim_entity'][0]['entity_id']}]")
        for t, n in counts.items():
            print(f"  {t}: {n} row(s)")
    text = json.dumps(tables, indent=2)
    if a.out_json:
        with open(a.out_json, "w") as fh:
            fh.write(text + "\n")
        print(f"wrote {a.out_json}")
    if not a.out_dir and not a.out_json:
        sys.stdout.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
