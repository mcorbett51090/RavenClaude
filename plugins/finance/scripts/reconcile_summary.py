#!/usr/bin/env python3
"""reconcile_summary.py - balance-sheet tie-out status + period-over-period flux.

The two controller-review artifacts that WRAP the statements in a close package:

  reconcile  Each balance-sheet account's book balance vs an optional sub-ledger /
             third-party balance. Within materiality -> PASS (review-by-exception,
             the discipline behind FloQast/Numeric auto-certification); a break at
             or beyond materiality -> FLAG for a human. Accounts with no sub-ledger
             are marked 'self-supported' rather than silently passed.

  flux       Period-over-period movement per account, materiality-suppressed so the
             controller reads the handful of lines that MOVED, not the whole TB.
             This produces the movement table; the NARRATIVE 'why' is authored via
             the existing skills/variance-commentary skill + finance_calc.py
             variance-bridge (house rule: reuse, don't duplicate the flux skill).

Materiality is read from the entity profile (materiality_threshold). Reconciliation
before commentary (finance CLAUDE.md sec.3 #3): flux on an un-reconciled account
describes noise, not signal. Stdlib only. Python 3.8+.
"""
from __future__ import annotations

import argparse
import csv
import json


def _read_csv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _tb_net(path):
    """account -> (description, net book balance = debit - credit)."""
    out = {}
    for row in _read_csv(path):
        acct = (row.get("account") or "").strip()
        if not acct:
            continue
        net = float(row.get("debit") or 0) - float(row.get("credit") or 0)
        out[acct] = ((row.get("description") or "").strip(), round(net, 2))
    return out


def reconcile(tb_path, materiality, subledger_path=None):
    tb = _tb_net(tb_path)
    subs = {}
    if subledger_path:
        for row in _read_csv(subledger_path):
            subs[(row.get("account") or "").strip()] = round(float(row.get("subledger_balance") or 0), 2)
    rows = []
    flagged = 0
    for acct, (desc, book) in sorted(tb.items()):
        if acct in subs:
            diff = round(book - subs[acct], 2)
            status = "PASS" if abs(diff) < materiality else "FLAG"
            if status == "FLAG":
                flagged += 1
            rows.append({"account": acct, "description": desc, "book_balance": book,
                         "subledger_balance": subs[acct], "difference": diff, "status": status})
        else:
            rows.append({"account": acct, "description": desc, "book_balance": book,
                         "subledger_balance": None, "difference": None,
                         "status": "self-supported"})
    return {"materiality_threshold": materiality, "flagged_count": flagged, "accounts": rows}


def flux(tb_path, prior_tb_path, materiality):
    cur, prior = _tb_net(tb_path), _tb_net(prior_tb_path)
    movements = []
    for acct in sorted(set(cur) | set(prior)):
        desc = (cur.get(acct) or prior.get(acct))[0]
        c = cur.get(acct, (desc, 0.0))[1]
        p = prior.get(acct, (desc, 0.0))[1]
        move = round(c - p, 2)
        if abs(move) >= materiality:
            pct = (move / p * 100) if p else None
            movements.append({"account": acct, "description": desc, "current": c,
                              "prior": p, "movement": move,
                              "pct_change": round(pct, 1) if pct is not None else None})
    movements.sort(key=lambda m: abs(m["movement"]), reverse=True)
    return {"materiality_threshold": materiality, "suppressed_below": materiality,
            "material_movements": movements}


def main(argv=None):
    p = argparse.ArgumentParser(description="Reconciliation tie-out + period flux for the close.")
    p.add_argument("--entity", required=True)
    p.add_argument("--tb", required=True)
    p.add_argument("--prior-tb")
    p.add_argument("--subledger")
    p.add_argument("--out")
    a = p.parse_args(argv)
    with open(a.entity) as fh:
        entity = json.load(fh)
    mat = float(entity.get("materiality_threshold", 0))
    result = {"entity": entity["entity_name"], "period": entity["fiscal_period"],
              "reconciliation": reconcile(a.tb, mat, a.subledger)}
    if a.prior_tb:
        result["flux"] = flux(a.tb, a.prior_tb, mat)
    text = json.dumps(result, indent=2)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text + "\n")
        fc = result["reconciliation"]["flagged_count"]
        print(f"wrote {a.out}  reconciliation flags: {fc}"
              + (f"  material movements: {len(result['flux']['material_movements'])}" if a.prior_tb else ""))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
