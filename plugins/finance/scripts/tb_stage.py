#!/usr/bin/env python3
"""tb_stage.py - normalize a raw accounting-system TB export into the CANONICAL staging schema.

WHAT THIS IS (and is NOT). This is the finance-shaped ELT *staging* seam: the thin,
deterministic transform that turns a vendor's raw trial-balance export (QuickBooks
Online, NetSuite, Xero, Sage Intacct — each with its own column names, sign
conventions, and dimensions) into the ONE canonical table the rest of the close
autopilot consumes. The canonical columns are, EXACTLY and in this order:

    account,description,debit,credit,entity,period,currency

That header is load-bearing: it is byte-identical to the columns a dbt staging model
(`stg_trial_balance`) would materialize, so a locally-staged CSV and the warehouse
staging table are the SAME contract. `statement_engine.py` / `reconcile_summary.py`
read exactly these columns — this script is what lets a real export flow into them
without hand-editing headers. The "local CSV == staging columns" equality is the
whole point; do not reorder or rename the canonical header.

Three disciplines keep it honest:

  1. ONE ADAPTER, DATA-DRIVEN PER SOURCE. There is no per-vendor code path. A source
     is described by a *column-map JSON* (canonical column -> source column, plus an
     optional signed-`amount_column` split for sources that emit one signed net
     figure instead of separate debit/credit). QBO/NetSuite/Xero/Intacct differ only
     in their column-map, never in this file.

  2. DIMENSIONS + A CLOSE-PERIOD WATERMARK ARE STAMPED, NOT ASSUMED. `entity` and
     `currency` are added as explicit dimensions (so a multi-entity / multi-currency
     staging table can be filtered downstream), and every row is stamped with the
     `period` being closed — the close-period watermark that makes the staging table
     partitionable / incrementally loadable by close period.

  3. BLOCK ON A BAD EXPORT; WRITE ATOMICALLY. `stage` validates its own output before
     it publishes it — canonical header, numeric debit/credit, non-blank dimensions +
     watermark, and the fundamental trial-balance invariant debits == credits — and
     REFUSES (non-zero exit) to emit a staging file that fails any of them, rather
     than silently landing a broken TB. The write is atomic (temp file + os.replace)
     so a reader never sees a half-written staging file.

SCOPE / TIER CAVEAT — READ THIS. This is *scaffolding*. No live credentials are used
or required here: extraction from a vendor API (OAuth2, rotating refresh tokens, rate
limits) is a separate, credentialed tier — its blocking facts + failure modes live in
`../knowledge/finance-elt-connector-facts.md` and the per-entity wiring in
`../templates/connector-config.template.json`. This module operates on a raw export
FILE that a connector already produced. Output is decision-support, not an
accounting/audit/tax opinion (../CLAUDE.md sec.3).

Stdlib only (csv/json/argparse/os/sys). Python 3.8+.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys

# The canonical staging contract — EXACT names, EXACT order. Byte-identical to the
# dbt staging model's columns. Everything downstream keys off this.
CANONICAL = ["account", "description", "debit", "credit", "entity", "period", "currency"]
NUMERIC = ("debit", "credit")
# Canonical columns that are dimensions/watermark, sourced from config when a raw
# export doesn't carry them per-row.
STATIC_CANDIDATES = ("entity", "currency", "period")


def _num(raw) -> float:
    """Parse a possibly-messy money string to a float. Handles $, thousands commas,
    and accounting parens for negatives. Blank / '-' -> 0.0. Raises ValueError on junk."""
    s = (raw or "").strip()
    if s in ("", "-", "--"):
        return 0.0
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1]
    s = s.replace("$", "").replace(",", "").replace(" ", "")
    if s.startswith("-"):
        neg = True
        s = s[1:]
    val = float(s)
    return -val if neg else val


def _fmt(n: float) -> str:
    """Deterministic money formatting for a staging cell: whole numbers as ints,
    otherwise 2dp. Keeps the staged CSV byte-stable across runs."""
    n = round(n + 0.0, 2)
    return str(int(n)) if n == int(n) else f"{n:.2f}"


def load_column_map(path: str) -> dict:
    """Load + shape-check a per-source column-map JSON.

    Recognized keys:
      map            {canonical_col: source_col}  (at minimum account, description)
      amount_column  source col holding ONE signed net amount, split into debit/credit
      amount_sign    "debit_positive" (default) | "credit_positive"
      constants      {canonical_col: literal}     (typically entity, currency)
      close_period   the watermark value written into every row's `period` column
    """
    try:
        with open(path) as fh:
            cm = json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"cannot read column-map {path}: {e}")
    if not isinstance(cm.get("map"), dict):
        raise SystemExit(f"{path}: column-map must contain an object 'map' (canonical -> source column)")
    sign = cm.get("amount_sign", "debit_positive")
    if sign not in ("debit_positive", "credit_positive"):
        raise SystemExit(f"{path}: amount_sign must be 'debit_positive' or 'credit_positive', got {sign!r}")
    return cm


def _resolve_statics(cm: dict, overrides: dict) -> dict:
    """Merge config-supplied statics (constants + close_period watermark) with CLI
    overrides. CLI wins so one column-map can be reused across periods/entities."""
    statics: dict[str, str] = {}
    consts = cm.get("constants") or {}
    if not isinstance(consts, dict):
        raise SystemExit("column-map 'constants' must be an object")
    for k, v in consts.items():
        statics[k] = str(v)
    if cm.get("close_period") is not None:
        statics["period"] = str(cm["close_period"])
    for k, v in overrides.items():
        if v is not None:
            statics[k] = str(v)
    return statics


def _plan(cm: dict, statics: dict) -> dict:
    """Decide, per canonical column, where its value comes from. Fails closed if any
    canonical column is unresolved — a staging file must be COMPLETE by construction."""
    src_map = cm["map"]
    amount_col = cm.get("amount_column")
    plan: dict[str, tuple] = {}
    unresolved = []
    for col in CANONICAL:
        if col in NUMERIC and amount_col:
            plan[col] = ("amount", amount_col, cm.get("amount_sign", "debit_positive"))
        elif col in src_map:
            plan[col] = ("column", src_map[col], None)
        elif col in statics:
            plan[col] = ("static", statics[col], None)
        else:
            unresolved.append(col)
    if unresolved:
        raise SystemExit(
            "column-map does not resolve every canonical column: "
            + ", ".join(unresolved)
            + " (add them to 'map', 'constants'/'close_period', or pass --entity/--currency/--period)"
        )
    return plan


def _split_amount(amt: float, sign: str) -> tuple:
    """Split one signed net amount into (debit, credit). Under 'debit_positive' a
    positive amount is a debit; under 'credit_positive' a positive amount is a credit."""
    if sign == "credit_positive":
        amt = -amt
    return (amt, 0.0) if amt >= 0 else (0.0, -amt)


def stage_rows(raw_path: str, cm: dict, statics: dict) -> list:
    """Read the raw export and emit canonical rows (list-of-lists in CANONICAL order)."""
    plan = _plan(cm, statics)
    out_rows = []
    with open(raw_path, newline="") as fh:
        reader = csv.DictReader(fh)
        src_cols = set(reader.fieldnames or [])
        # Fail early if the map points at a source column the export doesn't have.
        needed = {spec[1] for spec in plan.values() if spec[0] in ("column", "amount")}
        missing = sorted(needed - src_cols)
        if missing:
            raise SystemExit(
                f"{raw_path}: raw export is missing source column(s) named in the column-map: "
                + ", ".join(repr(m) for m in missing)
                + f"  (export has: {sorted(src_cols)})"
            )
        for i, row in enumerate(reader, 2):
            cells = []
            for col in CANONICAL:
                kind, ref, sign = plan[col]
                if kind == "static":
                    cells.append(ref)
                elif kind == "amount":
                    try:
                        amt = _num(row.get(ref))
                    except ValueError:
                        raise SystemExit(f"{raw_path}:{i} non-numeric amount {row.get(ref)!r} in {ref!r}")
                    debit, credit = _split_amount(amt, sign)
                    cells.append(_fmt(debit if col == "debit" else credit))
                else:  # column
                    val = row.get(ref)
                    if col in NUMERIC:
                        try:
                            cells.append(_fmt(_num(val)))
                        except ValueError:
                            raise SystemExit(f"{raw_path}:{i} non-numeric {col} {val!r} in {ref!r}")
                    else:
                        cells.append((val or "").strip())
            out_rows.append(cells)
    return out_rows


def validate_staging(path: str) -> list:
    """Validate a CANONICAL staging CSV. Returns a list of error strings (empty == OK).

    Checks: exact canonical header (order matters — byte-identity to the dbt model),
    numeric debit/credit, non-blank account + entity/currency dimensions + period
    watermark, a single close period per file, and the TB invariant debits == credits."""
    errs: list[str] = []
    try:
        fh = open(path, newline="")
    except OSError as e:
        return [f"cannot read staging file {path}: {e}"]
    with fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != CANONICAL:
            return [
                f"column header {reader.fieldnames} != canonical {CANONICAL} "
                f"(staging must be byte-identical to the dbt staging model columns)"
            ]
        tot_d = tot_c = 0.0
        periods: set = set()
        n = 0
        for i, row in enumerate(reader, 2):
            n += 1
            if not (row.get("account") or "").strip():
                errs.append(f"line {i}: blank account")
            for col in NUMERIC:
                try:
                    v = _num(row.get(col))
                except ValueError:
                    errs.append(f"line {i}: non-numeric {col} {row.get(col)!r}")
                    v = 0.0
                if col == "debit":
                    tot_d += v
                else:
                    tot_c += v
            if not (row.get("entity") or "").strip():
                errs.append(f"line {i}: blank entity dimension")
            if not (row.get("currency") or "").strip():
                errs.append(f"line {i}: blank currency dimension")
            per = (row.get("period") or "").strip()
            if not per:
                errs.append(f"line {i}: blank period watermark")
            else:
                periods.add(per)
        if n == 0:
            errs.append("staging file has a header but no rows")
        if abs(round(tot_d - tot_c, 2)) >= 0.01:
            errs.append(
                f"OUT OF BALANCE: debits {tot_d:,.2f} != credits {tot_c:,.2f} "
                f"(delta {tot_d - tot_c:,.2f}) — a trial balance must balance before it stages"
            )
        if len(periods) > 1:
            errs.append(
                f"multiple close periods in one staging file: {sorted(periods)} "
                f"(a staging load should carry ONE close-period watermark)"
            )
    return errs


def _atomic_write(path: str, rows: list) -> None:
    """Write header + rows to `path` atomically (temp file + os.replace)."""
    parent = os.path.dirname(os.path.abspath(path))
    os.makedirs(parent, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(CANONICAL)
        w.writerows(rows)
    os.replace(tmp, path)


def cmd_stage(a) -> int:
    cm = load_column_map(a.column_map)
    statics = _resolve_statics(cm, {"entity": a.entity, "currency": a.currency, "period": a.period})
    rows = stage_rows(a.raw, cm, statics)
    # Validate BEFORE publishing: write to a scratch temp, validate it, and only then
    # promote. This is the block-on-bad-export discipline + the atomic write together.
    scratch = a.out + ".staging-tmp"
    with open(scratch, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(CANONICAL)
        w.writerows(rows)
    errs = validate_staging(scratch)
    if errs:
        os.remove(scratch)
        sys.stderr.write(f"BLOCKED: raw export {a.raw} does not stage to a valid trial balance:\n")
        for e in errs:
            sys.stderr.write(f"  - {e}\n")
        return 4
    os.replace(scratch, a.out)   # atomic promote
    tot_d = sum(_num(r[2]) for r in rows)
    print(f"wrote {a.out}  [{len(rows)} accounts, balanced at {tot_d:,.2f} "
          f"{statics.get('currency', '?')}, period {statics.get('period', '?')}]")
    return 0


def cmd_validate(a) -> int:
    errs = validate_staging(a.staging)
    if errs:
        sys.stderr.write(f"INVALID staging file {a.staging}:\n")
        for e in errs:
            sys.stderr.write(f"  - {e}\n")
        return 1
    print(f"OK: {a.staging} is canonical, balanced, and dimension/watermark-complete.")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Normalize a raw accounting-system TB export into the canonical staging schema."
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("stage", help="normalize a raw export -> canonical staging CSV (blocks on a bad export)")
    s.add_argument("--raw", required=True, help="raw vendor TB export CSV")
    s.add_argument("--column-map", required=True, help="per-source column-map JSON")
    s.add_argument("--out", required=True, help="canonical staging CSV to write (atomically)")
    s.add_argument("--entity", help="override/supply the entity dimension")
    s.add_argument("--currency", help="override/supply the currency dimension")
    s.add_argument("--period", help="override/supply the close-period watermark")

    v = sub.add_parser("validate", help="validate a canonical staging CSV (columns/types + debits==credits)")
    v.add_argument("--staging", required=True, help="canonical staging CSV to check")

    a = p.parse_args(argv)
    try:
        if a.cmd == "stage":
            return cmd_stage(a)
        if a.cmd == "validate":
            return cmd_validate(a)
    except SystemExit as e:
        if isinstance(e.code, str):
            sys.stderr.write(e.code + "\n")
            return 2
        return e.code or 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
