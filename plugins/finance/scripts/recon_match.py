#!/usr/bin/env python3
"""recon_match.py - reconciliation auto-match + threshold auto-certification.

WHAT THIS IS. The static reconcile_summary.py compares a book balance to a single
sub-ledger *total* and flags the delta. That is the tie-out READOUT; it cannot say
*which lines* explain the difference, so a human still eyeballs every account. This
module is the auto-MATCH engine that closes that gap — the FloQast AutoRec / Numeric
discipline: pair GL journal lines to sub-ledger / bank lines, explain the difference
line-by-line, and AUTO-CERTIFY (review-by-exception) only the accounts whose
UNexplained residual is within the entity's materiality threshold. Everything else
is FLAGGED for a human, who owns it.

THE MATCH LADDER (greedy, in order, deterministic — earlier stages win):
  1. exact     same reference AND amount equal to the cent.
  2. tolerance same reference AND |amount delta| <= --tolerance (bank rounding, FX
               pennies, a fee netted on one side). The delta is recorded, not hidden.
  3. grouped   many-to-one / one-to-many: remaining lines that SHARE a reference,
               where the group's GL sum ties to its sub-ledger sum within tolerance
               (e.g. two partial receipts booked against one deposit).
  Anything still unmatched is a BREAK.

RESIDUAL, DEFINED. For each account:
    residual = GL_total - subledger_total - matched_delta
where matched_delta is the net (GL - sub) across every matched pair/group (0 for an
exact match, the epsilon for a tolerance match, the group net for a grouped match).
By construction this equals (unmatched GL) - (unmatched sub) — i.e. the residual is
exactly the net of the BREAK items; matched lines cancel. The engine asserts that
identity every run as an independent cross-check (cf. statement_engine's NI check).

AUTO-CERTIFICATION IS MATERIALITY-BOUNDED, NOT ZERO-BREAK.
  |residual| <  materiality  -> AUTO-CERTIFIED (review-by-exception). An account can
                                auto-certify while still carrying an IMMATERIAL
                                unmatched item — the item is disclosed in the trail,
                                it just does not warrant a human's time.
  |residual| >= materiality  -> FLAGGED. A human controller owns it; --strict makes
                                the whole run exit non-zero so the close cannot
                                advance past an un-cleared material break.

Every auto-cert carries an EXPLAINABLE match trail (which GL lines matched which
sub-ledger lines, at which stage, with what delta, and the residual) so the
certification is auditable, not a black box.

HONEST SCOPE. Both inputs must be presented on a CONSISTENT sign basis (both signed
so that a positive on each side means the same direction) — this engine compares two
independently-sourced amounts, it does not re-derive presentation signs from a COA
section the way statement_engine.py does. Output is decision-support, not an audit
opinion or a GAAP determination (../CLAUDE.md sec.3): auto-certification bounds a
human's attention by materiality; it does not certify the underlying transactions.

Stdlib only (csv/json/argparse). Python 3.8+.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys

EXACT_EPS = 0.005          # "equal to the cent"
DEFAULT_TOLERANCE = 1.00   # bank rounding / FX pennies band for a tolerance match


def _read_csv(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def load_lines(path: str, side: str) -> list[dict]:
    """Read a GL or sub-ledger line CSV: account,reference,amount[,description]."""
    out: list[dict] = []
    for i, row in enumerate(_read_csv(path), 2):
        acct = (row.get("account") or "").strip()
        if not acct:
            continue
        try:
            amount = round(float(row.get("amount") or 0), 2)
        except ValueError:
            raise SystemExit(f"{path}:{i} non-numeric amount for account {acct!r}")
        out.append({
            "id": f"{side}#{len(out) + 1}",
            "side": side,
            "account": acct,
            "reference": (row.get("reference") or "").strip(),
            "amount": amount,
            "description": (row.get("description") or "").strip(),
            "matched": False,
        })
    return out


def _by_account(lines: list[dict]) -> dict:
    grouped: dict[str, list[dict]] = {}
    for ln in lines:
        grouped.setdefault(ln["account"], []).append(ln)
    return grouped


def _line_ref(ln: dict) -> dict:
    """Compact, trail-safe view of a line (no internal mutable flags)."""
    return {"id": ln["id"], "reference": ln["reference"],
            "amount": ln["amount"], "description": ln["description"]}


def match_account(gl: list[dict], sub: list[dict], tolerance: float) -> dict:
    """Run the match ladder over one account's lines. Returns the account result."""
    matches: list[dict] = []

    def _record(mtype, gl_lines, sub_lines):
        for ln in gl_lines + sub_lines:
            ln["matched"] = True
        g_amt = round(sum(x["amount"] for x in gl_lines), 2)
        s_amt = round(sum(x["amount"] for x in sub_lines), 2)
        matches.append({
            "type": mtype,
            "reference": (gl_lines or sub_lines)[0]["reference"],
            "gl": [_line_ref(x) for x in gl_lines],
            "subledger": [_line_ref(x) for x in sub_lines],
            "gl_amount": g_amt,
            "subledger_amount": s_amt,
            "delta": round(g_amt - s_amt, 2),
        })

    # Stage 1 — exact (reference + amount to the cent).
    for g in gl:
        if g["matched"]:
            continue
        for s in sub:
            if s["matched"] or s["reference"] != g["reference"]:
                continue
            if abs(g["amount"] - s["amount"]) < EXACT_EPS:
                _record("exact", [g], [s])
                break

    # Stage 2 — tolerance (reference + amount within the epsilon band).
    for g in gl:
        if g["matched"]:
            continue
        for s in sub:
            if s["matched"] or s["reference"] != g["reference"]:
                continue
            if abs(g["amount"] - s["amount"]) <= tolerance:
                _record("tolerance", [g], [s])
                break

    # Stage 3 — grouped (many-to-one / one-to-many by shared reference).
    gl_groups: dict[str, list[dict]] = {}
    sub_groups: dict[str, list[dict]] = {}
    for g in gl:
        if not g["matched"] and g["reference"]:
            gl_groups.setdefault(g["reference"], []).append(g)
    for s in sub:
        if not s["matched"] and s["reference"]:
            sub_groups.setdefault(s["reference"], []).append(s)
    for ref in sorted(gl_groups):
        if ref not in sub_groups:
            continue
        gsum = round(sum(x["amount"] for x in gl_groups[ref]), 2)
        ssum = round(sum(x["amount"] for x in sub_groups[ref]), 2)
        if abs(gsum - ssum) <= tolerance:
            _record("grouped", gl_groups[ref], sub_groups[ref])

    breaks = [
        {"side": ln["side"], "reference": ln["reference"], "amount": ln["amount"],
         "description": ln["description"]}
        for ln in gl + sub if not ln["matched"]
    ]

    gl_total = round(sum(x["amount"] for x in gl), 2)
    sub_total = round(sum(x["amount"] for x in sub), 2)
    matched_delta = round(sum(m["delta"] for m in matches), 2)
    residual = round(gl_total - sub_total - matched_delta, 2)

    # Independent cross-check: residual must equal the net of the unmatched (break)
    # items. Matched pairs cancel by construction; if this fails the ladder is buggy.
    unmatched_gl = round(sum(x["amount"] for x in gl if not x["matched"]), 2)
    unmatched_sub = round(sum(x["amount"] for x in sub if not x["matched"]), 2)
    assert abs(residual - round(unmatched_gl - unmatched_sub, 2)) < 0.01, \
        "residual != net of unmatched breaks (match-ladder invariant violated)"

    return {
        "gl_total": gl_total,
        "subledger_total": sub_total,
        "matched_delta": matched_delta,
        "residual": residual,
        "matches": matches,
        "breaks": breaks,
    }


def reconcile(gl_lines: list[dict], sub_lines: list[dict], materiality: float,
              tolerance: float) -> dict:
    gl_by = _by_account(gl_lines)
    sub_by = _by_account(sub_lines)
    accounts = []
    tallies = {"exact": 0, "tolerance": 0, "grouped": 0}
    n_breaks = 0
    n_auto = 0
    n_flag = 0
    for acct in sorted(set(gl_by) | set(sub_by)):
        res = match_account(gl_by.get(acct, []), sub_by.get(acct, []), tolerance)
        auto = abs(res["residual"]) < materiality
        status = "AUTO-CERTIFIED" if auto else "FLAGGED"
        if auto:
            n_auto += 1
            cert = (f"review-by-exception: unexplained residual "
                    f"{res['residual']:,.2f} within materiality {materiality:,.2f}"
                    f" — auto-certified.")
        else:
            n_flag += 1
            cert = (f"FLAG for human: unexplained residual {res['residual']:,.2f} "
                    f">= materiality {materiality:,.2f} — a controller must clear it.")
        for m in res["matches"]:
            tallies[m["type"]] += 1
        n_breaks += len(res["breaks"])
        accounts.append({"account": acct, "status": status, **res,
                         "certification": cert})
    tallies["total"] = tallies["exact"] + tallies["tolerance"] + tallies["grouped"]
    return {
        "materiality_threshold": materiality,
        "tolerance": tolerance,
        "summary": {
            "accounts": len(accounts),
            "auto_certified": n_auto,
            "flagged": n_flag,
            "matches": tallies,
            "breaks": n_breaks,
        },
        "accounts": accounts,
        "disclaimer": (
            "Auto-certification is materiality-bounded decision-support, not an audit "
            "opinion or a GAAP determination. Every FLAGGED account is owned by a human "
            "controller; an AUTO-CERTIFIED account may still carry an immaterial "
            "unmatched item, disclosed in its match trail for review-by-exception."
        ),
    }


def run(entity: dict, gl_path: str, sub_path: str, tolerance: float,
        materiality_override=None) -> dict:
    materiality = (float(materiality_override) if materiality_override is not None
                   else float(entity.get("materiality_threshold", 0)))
    result = reconcile(load_lines(gl_path, "GL"), load_lines(sub_path, "SUB"),
                       materiality, tolerance)
    result = {"entity": entity.get("entity_name"),
              "period": entity.get("fiscal_period"), **result}
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Reconciliation auto-match + threshold auto-certification.")
    p.add_argument("--entity", required=True, help="entity profile JSON (materiality source)")
    p.add_argument("--gl", required=True, help="GL journal-line CSV: account,reference,amount[,description]")
    p.add_argument("--subledger", required=True, help="sub-ledger / bank line CSV (same columns)")
    p.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE,
                   help=f"amount epsilon for a tolerance/grouped match (default {DEFAULT_TOLERANCE})")
    p.add_argument("--materiality", type=float, default=None,
                   help="override the entity's materiality_threshold")
    p.add_argument("--strict", action="store_true",
                   help="exit non-zero if any account is FLAGGED (blocks the close)")
    p.add_argument("--out", help="write result JSON here (else stdout)")
    a = p.parse_args(argv)

    with open(a.entity) as fh:
        entity = json.load(fh)
    result = run(entity, a.gl, a.subledger, a.tolerance, a.materiality)
    text = json.dumps(result, indent=2)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text + "\n")
        s = result["summary"]
        print(f"wrote {a.out}  auto-certified {s['auto_certified']}/{s['accounts']} "
              f"accounts, flagged {s['flagged']}, breaks {s['breaks']}, "
              f"matches {s['matches']['total']}")
    else:
        print(text)

    if a.strict and result["summary"]["flagged"]:
        sys.stderr.write(
            f"BLOCKED (--strict): {result['summary']['flagged']} account(s) FLAGGED "
            f"above materiality — a human controller must clear them before the close "
            f"can advance.\n")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
