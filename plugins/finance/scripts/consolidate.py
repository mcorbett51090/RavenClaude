#!/usr/bin/env python3
"""consolidate.py - multi-entity roll-up with intercompany elimination.

WHAT THIS IS (and is NOT). Rolling N single-entity trial balances into a group
consolidation is a governed-close problem, not a spreadsheet SUM. The dangerous
part is not the addition — it is the ELIMINATION: two legal entities each book
their side of an intercompany transaction (a loan, an internal sale), so a naive
sum DOUBLE-COUNTS it. Consolidated statements must show only what the group
transacted with the *outside world*. The auditor's mantra is "eliminate before
you consolidate," and this engine enforces exactly that order:

  1. PRODUCE each entity's statements by REUSING statement_engine.run — same
     classification discipline, same SECTION-based presentation sign (so a
     contra-account or an intercompany line is signed by its section's natural
     side, never by the account's normal_balance). Consolidation adds no new
     accounting-sign logic; it composes the engine that already got it right.

  2. SUM by statement line across entities into a worksheet (one column per
     entity). This is the pre-elimination total — and it still contains the
     intercompany balances on BOTH sides. That double-count is the whole reason
     step 3 exists; the worksheet surfaces it rather than hiding it.

  3. ELIMINATE from an intercompany-transactions CSV expressed as a BALANCED
     elimination journal (Σ debits == Σ credits, asserted). Each elimination
     amount is converted to a presentation sign with the SAME section convention,
     so IC receivable/payable and IC revenue/COGS each net to 0.00 in the
     consolidated column. Because the elimination journal balances, the
     consolidated balance sheet still balances to 0.00 — asserted, not assumed.

  4. FLAG currency translation (CTA). An entity whose functional currency differs
     from the group's presentation currency needs a real remeasurement (assets at
     closing rate, income at average rate, equity at historical rate, the plug to
     a CTA component of equity/OCI). This engine does NOT perform that
     remeasurement — it FLAGS the entity and emits an honest CTA note. Treating a
     provided non-functional-currency trial balance as if already in the
     presentation currency is a simplification, stated plainly on the artifact.

Reusable per group: entities and the group are DATA (a consolidation config JSON
+ per-entity profiles + trial balances + one IC-eliminations CSV). The code
carries no group-specific fact. Stdlib only (csv/json/argparse). Python 3.8+.

Outputs are decision-support, NOT an audited consolidation, a GAAP/IFRS
determination, or a multi-currency remeasurement (../CLAUDE.md sec.3, sec.12).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import entity_config as ec  # noqa: E402
import statement_engine as se  # noqa: E402

# Section ordering for a readable worksheet (mirrors statement_engine's sets).
IS_SECTION_ORDER = ["Revenue", "COGS", "OpEx", "OtherIncomeExpense", "Tax"]
BS_SECTION_ORDER = [
    "CurrentAssets",
    "NonCurrentAssets",
    "CurrentLiabilities",
    "NonCurrentLiabilities",
    "Equity",
]
ASSET_SECTIONS = {"CurrentAssets", "NonCurrentAssets"}
LIABILITY_SECTIONS = {"CurrentLiabilities", "NonCurrentLiabilities"}


def _resolve(base_dir: str, path: str) -> str:
    """Resolve a config-relative path against the config file's directory."""
    return path if os.path.isabs(path) else os.path.join(base_dir, path)


def load_config(path: str) -> dict:
    with open(path) as fh:
        cfg = json.load(fh)
    if cfg.get("schema_version") != 1:
        raise SystemExit(
            f"{path}: schema_version must be 1, got "
            f"{cfg.get('schema_version')!r} (re-review the config)"
        )
    if not cfg.get("entities"):
        raise SystemExit(f"{path}: config lists no entities")
    if not cfg.get("group_name"):
        raise SystemExit(f"{path}: config is missing required key 'group_name'")
    return cfg


def run_entities(cfg: dict, base_dir: str, strict: bool):
    """Produce each entity's statements via statement_engine, validating profiles.

    Returns (results, period, cta_flags) where results is a list of
    {name, currency, statements} dicts.
    """
    presentation_ccy = cfg.get("presentation_currency", "USD")
    period = cfg.get("fiscal_period")
    results = []
    cta_flags = []
    for ent in cfg["entities"]:
        profile_path = _resolve(base_dir, ent["profile"])
        coa_path = _resolve(base_dir, ent["coa"])
        tb_path = _resolve(base_dir, ent["tb"])
        profile = ec.load(profile_path)
        errs = ec.validate(profile)
        if errs:
            sys.stderr.write(f"BLOCKED: invalid entity profile {profile_path}:\n")
            for e in errs:
                sys.stderr.write(f"  - {e}\n")
            raise SystemExit(2)
        # Fail-closed period check: if the group config omits fiscal_period, DERIVE it
        # from the first entity's profile, then assert EVERY entity matches. This closes
        # the hole where a falsy group period skipped the guard, letting entities from
        # different periods be silently rolled up.
        if period is None:
            period = profile.get("fiscal_period")
        if profile.get("fiscal_period") != period:
            raise SystemExit(
                f"BLOCKED: period mismatch — group period is {period!r} but "
                f"{profile['entity_name']!r} is {profile.get('fiscal_period')!r}. "
                f"A consolidation rolls up ONE period across entities."
            )
        stmts = se.run(profile, coa_path, tb_path, strict=strict)
        results.append(
            {
                "name": profile["entity_name"],
                "currency": profile["functional_currency"],
                "role": ent.get("role", ""),
                "statements": stmts,
            }
        )
        if profile["functional_currency"] != presentation_ccy:
            cta_flags.append(
                {
                    "entity": profile["entity_name"],
                    "functional_currency": profile["functional_currency"],
                    "presentation_currency": presentation_ccy,
                }
            )
    return results, presentation_ccy, cta_flags


def _trail_by_line(results):
    """Aggregate every entity's reasoning trail into worksheet line rows.

    Key = (statement, section, line). Value carries the per-entity presentation
    amount. Reusing statement_engine's reasoning trail means the presentation
    sign is exactly the section-based one the engine already computed — no
    re-derivation, no second sign convention to keep in step.
    """
    lines: dict = {}
    names = [r["name"] for r in results]
    for r in results:
        trail = r["statements"]["reasoning_trail"]
        for stmt, entries in (("IS", trail["income_statement"]), ("BS", trail["balance_sheet"])):
            for e in entries:
                key = (stmt, e["section"], e["line"])
                slot = lines.setdefault(
                    key,
                    {
                        "statement": stmt,
                        "section": e["section"],
                        "line": e["line"],
                        "entities": dict.fromkeys(names, 0.0),
                        "elimination": 0.0,
                    },
                )
                slot["entities"][r["name"]] = round(slot["entities"][r["name"]] + e["amount"], 2)
    return lines, names


def load_eliminations(path: str):
    """Read the IC-elimination journal; return (rows, debit_total, credit_total).

    Each row: {ic_id, description, statement, section, line, debit, credit} plus a
    computed section-signed `presentation_amount`. The journal MUST balance.
    """
    rows = []
    dtot = ctot = 0.0
    for i, raw in enumerate(se._read_csv(path), 2):
        section = (raw.get("section") or "").strip()
        try:
            debit = float(raw.get("debit") or 0)
            credit = float(raw.get("credit") or 0)
        except ValueError:
            raise SystemExit(f"{path}:{i} non-numeric debit/credit")
        # Reuse the engine's section-based presentation sign (contra-safe).
        pres = se._present({"debit": debit, "credit": credit}, section)
        rows.append(
            {
                "ic_id": (raw.get("ic_id") or "").strip(),
                "description": (raw.get("description") or "").strip(),
                "statement": (raw.get("statement") or "").strip(),
                "section": section,
                "line": (raw.get("line") or "").strip(),
                "debit": debit,
                "credit": credit,
                "presentation_amount": round(pres, 2),
            }
        )
        dtot += debit
        ctot += credit
    return rows, round(dtot, 2), round(ctot, 2)


def apply_eliminations(lines: dict, elim_rows: list) -> list:
    """Fold elimination amounts into the worksheet; block on unmatched lines."""
    errs = []
    for row in elim_rows:
        key = (row["statement"], row["section"], row["line"])
        if key not in lines:
            errs.append(
                f"elimination line {row['line']!r} (section {row['section']!r}, "
                f"{row['statement']}) matches no entity line — check spelling / "
                f"that the intercompany accounts are actually mapped and booked"
            )
            continue
        lines[key]["elimination"] = round(lines[key]["elimination"] + row["presentation_amount"], 2)
    return errs


def _section_totals(lines: dict, column: str):
    """Sum a worksheet column into section totals.

    column: 'pre' (sum of entity columns only) or 'consolidated' (with eliminations).
    """
    tot: dict = {}
    for slot in lines.values():
        entity_sum = round(sum(slot["entities"].values()), 2)
        val = entity_sum if column == "pre" else round(entity_sum + slot["elimination"], 2)
        tot[slot["section"]] = round(tot.get(slot["section"], 0.0) + val, 2)
    return tot


def _income_subtotals(sect: dict) -> dict:
    rev = round(sect.get("Revenue", 0.0), 2)
    cogs = round(sect.get("COGS", 0.0), 2)
    opex = round(sect.get("OpEx", 0.0), 2)
    other = round(sect.get("OtherIncomeExpense", 0.0), 2)
    tax = round(sect.get("Tax", 0.0), 2)
    gross = round(rev - cogs, 2)
    oi = round(gross - opex, 2)
    pretax = round(oi + other, 2)
    ni = round(pretax - tax, 2)
    return {
        "revenue": rev,
        "cogs": cogs,
        "gross_profit": gross,
        "operating_expenses": opex,
        "operating_income": oi,
        "other_income_expense_net": other,
        "pretax_income": pretax,
        "income_tax_expense": tax,
        "net_income": ni,
    }


def _balance_subtotals(sect: dict, net_income: float) -> dict:
    ca = round(sect.get("CurrentAssets", 0.0), 2)
    ta = round(sum(sect.get(s, 0.0) for s in ASSET_SECTIONS), 2)
    tl = round(sum(sect.get(s, 0.0) for s in LIABILITY_SECTIONS), 2)
    eq_beg = round(sect.get("Equity", 0.0), 2)
    teq = round(eq_beg + net_income, 2)
    return {
        "total_assets": ta,
        "total_current_assets": ca,
        "total_liabilities": tl,
        "equity_beginning": eq_beg,
        "current_period_net_income": round(net_income, 2),
        "total_equity": teq,
        "balance_delta": round(ta - (tl + teq), 2),
    }


def _worksheet_rows(lines: dict, names: list, statement: str, order: list) -> list:
    """Emit sorted worksheet rows for one statement (entity cols + elim + consolidated)."""
    rank = {s: i for i, s in enumerate(order)}
    rows = [s for s in lines.values() if s["statement"] == statement]
    rows.sort(key=lambda s: (rank.get(s["section"], 99), s["line"]))
    out = []
    for s in rows:
        entity_sum = round(sum(s["entities"].values()), 2)
        out.append(
            {
                "section": s["section"],
                "line": s["line"],
                "entities": {n: round(s["entities"][n], 2) for n in names},
                "eliminations": round(s["elimination"], 2),
                "consolidated": round(entity_sum + s["elimination"], 2),
            }
        )
    return out


def consolidate(config_path: str, strict: bool = True) -> dict:
    base_dir = os.path.dirname(os.path.abspath(config_path))
    cfg = load_config(config_path)
    results, presentation_ccy, cta_flags = run_entities(cfg, base_dir, strict)

    lines, names = _trail_by_line(results)

    elim_path = _resolve(base_dir, cfg["eliminations"]) if cfg.get("eliminations") else None
    elim_rows, dtot, ctot = ([], 0.0, 0.0)
    if elim_path:
        elim_rows, dtot, ctot = load_eliminations(elim_path)
        if abs(dtot - ctot) >= 0.01:
            sys.stderr.write(
                f"BLOCKED: elimination journal is out of balance — debits {dtot:,.2f} "
                f"!= credits {ctot:,.2f}. An unbalanced elimination would break the "
                f"consolidated balance sheet.\n"
            )
            raise SystemExit(4)
        match_errs = apply_eliminations(lines, elim_rows)
        if match_errs:
            sys.stderr.write("BLOCKED: elimination lines do not match the worksheet:\n")
            for e in match_errs:
                sys.stderr.write(f"  - {e}\n")
            raise SystemExit(5)

    # Subtotals: pre-elimination (double-counts IC) and consolidated (IC removed).
    pre_is = _income_subtotals(_section_totals(lines, "pre"))
    pre_bs = _balance_subtotals(_section_totals(lines, "pre"), pre_is["net_income"])
    con_is = _income_subtotals(_section_totals(lines, "consolidated"))
    con_bs = _balance_subtotals(_section_totals(lines, "consolidated"), con_is["net_income"])

    if abs(con_bs["balance_delta"]) >= 0.01:
        sys.stderr.write(
            f"BLOCKED: consolidated balance sheet does not balance — off by "
            f"{con_bs['balance_delta']:,.2f}. Assets must equal liabilities + equity "
            f"after eliminations.\n"
        )
        raise SystemExit(6)

    # Which lines were touched by an elimination, and did each net to zero?
    ic_lines = {}
    for row in elim_rows:
        key = (row["statement"], row["section"], row["line"])
        slot = lines.get(key)
        if slot is None:
            continue
        entity_sum = round(sum(slot["entities"].values()), 2)
        ic_lines[row["line"]] = {
            "pre_elimination": entity_sum,
            "eliminations": round(slot["elimination"], 2),
            "consolidated": round(entity_sum + slot["elimination"], 2),
        }

    return {
        "group": cfg["group_name"],
        "presentation_currency": presentation_ccy,
        "fiscal_period": cfg.get("fiscal_period"),
        "basis_badge": (
            "Consolidation from summarized entity trial balances — "
            "decision-support, NOT an audited consolidation or a full "
            "multi-currency remeasurement."
        ),
        "entities": [
            {"name": r["name"], "functional_currency": r["currency"], "role": r["role"]}
            for r in results
        ],
        "worksheet": {
            "income_statement": _worksheet_rows(lines, names, "IS", IS_SECTION_ORDER),
            "balance_sheet": _worksheet_rows(lines, names, "BS", BS_SECTION_ORDER),
        },
        "eliminations": {
            "journal": elim_rows,
            "debit_total": dtot,
            "credit_total": ctot,
            "balanced": abs(dtot - ctot) < 0.01,
            "intercompany_lines": ic_lines,
        },
        "pre_elimination_subtotals": {"income_statement": pre_is, "balance_sheet": pre_bs},
        "consolidated_subtotals": {"income_statement": con_is, "balance_sheet": con_bs},
        "currency_translation_note": {
            "flagged_entities": cta_flags,
            "caveat": (
                "Flagged entities report in a functional currency other than the "
                "group presentation currency. This engine does NOT perform a "
                "multi-currency remeasurement (closing/average/historical rates "
                "with the plug to a CTA component of equity/OCI). Their trial "
                "balances are treated as already stated in the presentation "
                "currency; a rigorous translation and its cumulative-translation-"
                "adjustment are OUT OF SCOPE and must be prepared separately."
            ),
        },
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Consolidate N entities with intercompany elimination.")
    p.add_argument("--config", required=True, help="consolidation config JSON")
    p.add_argument(
        "--no-strict",
        action="store_true",
        help="do NOT block on unmapped accounts in an entity (default: block)",
    )
    p.add_argument("--out", help="write consolidation JSON here (else stdout)")
    a = p.parse_args(argv)

    out = consolidate(a.config, strict=not a.no_strict)
    text = json.dumps(out, indent=2)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text + "\n")
        ni = out["consolidated_subtotals"]["income_statement"]["net_income"]
        delta = out["consolidated_subtotals"]["balance_sheet"]["balance_delta"]
        print(
            f"wrote {a.out}  [{len(out['entities'])} entities]  consolidated net "
            f"income {ni:,.2f} {out['presentation_currency']}  balance_delta {delta:,.2f}"
        )
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
