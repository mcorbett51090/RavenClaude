#!/usr/bin/env python3
"""remeasure.py - per-entity currency translation / remeasurement to a presentation TB.

WHAT THIS IS (and is NOT). consolidate.py flags a non-functional-currency entity and
emits an honest CTA note, but treats its trial balance as if already in the group's
presentation currency. That is a stated simplification. This stage removes it: it
translates ONE entity's functional-currency trial balance into a presentation-currency
(USD) trial balance that then flows into consolidate.py's worksheet BEFORE its
SystemExit-6 "consolidated balance sheet == 0.00" assertion (which STAYS the guardrail).

It composes statement_engine and adds NO new accounting-sign logic. The translated
debits/credits are pure arithmetic (functional amount x the rate its rate_class maps
to); the presentation SIGN of every line is statement_engine._present's section-based
convention, reused verbatim, and the subtotals + reasoning trail come from
statement_engine.build_income_statement / build_balance_sheet. The two supported
methods and their plug:

  CURRENT-RATE (translation, ASC 830 / IAS 21 "current rate").  All assets and
    liabilities at the CLOSING rate, income/expense at the AVERAGE rate, equity at
    HISTORICAL rates. The balancing plug is the cumulative translation adjustment
    (CTA), a component of OCI / equity - it does NOT touch net income.

  TEMPORAL (remeasurement, ASC 830 when the functional currency is the reporting
    currency).  MONETARY items at the CLOSING rate, NON-MONETARY items at HISTORICAL
    rates, P&L at the AVERAGE rate EXCEPT non-monetary-linked P&L (COGS, depreciation,
    prepaid amortization - rate_class REV_EXP_HIST) at HISTORICAL rates. The balancing
    plug is the remeasurement gain/(loss), which flows through NET INCOME.

The COA mapping gains a `rate_class` column in {MONETARY, NONMONETARY, EQUITY_CONTRIB,
EQUITY_RE, REV_EXP, REV_EXP_HIST}; a blank or invalid value BLOCKS the run exactly like
an unmapped account (statement_engine.lint_mapping discipline). Per-entity rates live in
a rates.json.

TWO refusals keep it honest:
  * A CTA SELF-CHECK: the balance-sheet-balancing plug MUST equal the analytical figure
    begin_net_assets x (closing - historical) + NI x (closing - average)
    - dividends x (closing - declaration), within 0.01, or the run BLOCKS. A plug that
    doesn't reconcile to the theory is a bug, not a CTA.
  * A highly_inflationary + current_rate combination is REFUSED: under ASC 830 a highly
    inflationary economy's books are remeasured as if the reporting currency were the
    functional currency (i.e. the temporal method), never translated at the current
    rate. IAS 29 (restate-for-inflation-then-translate) is a different answer and is
    OUT OF SCOPE here.

Zero-drift: when functional currency == presentation currency there is nothing to
translate, and the emitted trial balance is a BYTE-IDENTICAL copy of the input - so the
consolidate.py path is unchanged for an all-USD group.

Reusable per entity: the entity, its COA mapping (with rate_class), its trial balance,
and its rates.json are all DATA. The code carries no entity- or currency-specific fact.
Stdlib only (csv/json/argparse). Python 3.8+.

Outputs are decision-support, NOT an audited translation, a GAAP/IFRS determination, or
a live-rate-verified remeasurement. Sourcing the closing/average/historical rates, the
IdP/warehouse wiring, and any real credentials are the consumer's step (../CLAUDE.md
sec.3, sec.12).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import entity_config as ec  # noqa: E402
import statement_engine as se  # noqa: E402

RATE_CLASSES = {"MONETARY", "NONMONETARY", "EQUITY_CONTRIB", "EQUITY_RE", "REV_EXP", "REV_EXP_HIST"}
METHODS = {"current_rate", "temporal"}
EQUITY_CLASSES = {"EQUITY_CONTRIB", "EQUITY_RE"}

# Synthetic plug accounts injected into the translated TB (added to an in-memory copy
# of the mapping so statement_engine's builders classify them; never written to a COA).
CTA_ACCT = "__CTA__"
REMEAS_ACCT = "__REMEAS_GL__"
CTA_LINE = "Cumulative translation adjustment (CTA)"
REMEAS_LINE = "Remeasurement gain/(loss)"

# Exit codes (distinct from statement_engine's 3/4 and consolidate's 2-6 so a caller
# can tell WHY a translation blocked).
RC_MAPPING = 3  # rate_class missing/invalid or base mapping lint failure
RC_TB_UNBALANCED = 4  # functional trial balance is out of balance
RC_CTA_SELFCHECK = 5  # BS-balancing plug != analytical CTA
RC_ENTITY = 2  # invalid entity profile
RC_HYPERINFLATION = 7  # highly_inflationary + current_rate refused (ASC 830 vs IAS 29)
RC_RATES = 8  # rates.json missing/invalid a required rate key (closing/average/historical.default)


def load_mapping_with_rate_class(path: str) -> dict:
    """statement_engine.load_mapping + the new rate_class column (upper-cased)."""
    mapping = se.load_mapping(path)
    for row in se._read_csv(path):
        acct = (row.get("account") or "").strip()
        if acct in mapping:
            mapping[acct]["rate_class"] = (row.get("rate_class") or "").strip().upper()
    return mapping


def lint_rate_class(tb: list, mapping: dict) -> list:
    """rate_class coverage + coherence errors; block just like an unmapped account."""
    errs: list = []
    tb_accts = {r["account"] for r in tb}
    for acct in sorted(tb_accts):
        mp = mapping.get(acct)
        if mp is None:
            continue  # se.lint_mapping already reports the unmapped account
        rc = mp.get("rate_class", "")
        if rc not in RATE_CLASSES:
            errs.append(
                f"{acct}: rate_class must be one of {sorted(RATE_CLASSES)}, "
                f"got {rc!r} (blank/invalid blocks like an unmapped account)"
            )
            continue
        # Coherence: rate_class must agree with the account's statement/section.
        stmt, section = mp["statement"], mp["section"]
        if rc in EQUITY_CLASSES and (stmt != "BS" or section != "Equity"):
            errs.append(
                f"{acct}: rate_class {rc} requires a BS/Equity account, got {stmt}/{section}"
            )
        elif rc in ("MONETARY", "NONMONETARY") and (stmt != "BS" or section == "Equity"):
            errs.append(
                f"{acct}: rate_class {rc} requires a BS asset/liability account, "
                f"got {stmt}/{section}"
            )
        elif rc in ("REV_EXP", "REV_EXP_HIST") and stmt != "IS":
            errs.append(f"{acct}: rate_class {rc} requires an IS account, got {stmt}")
    return errs


def historical_rate(rates: dict, account: str) -> float:
    hist = rates.get("historical", {})
    if not isinstance(hist, dict) or "default" not in hist:
        raise SystemExit(
            "rates.historical must be an object with a 'default' key "
            "(and optional per-account overrides)"
        )
    return float(hist.get(account, hist["default"]))


def rate_for(method: str, rate_class: str, account: str, rates: dict) -> float:
    """The single rate a line is translated at, given the method + its rate_class.

    Pure lookup - the ONLY place the method's rate policy lives. No sign logic here;
    presentation signs stay with statement_engine._present.
    """
    closing, average = float(rates["closing"]), float(rates["average"])
    hist = historical_rate(rates, account)
    if method == "current_rate":
        # Translation: all A&L @ closing, all P&L @ average, equity @ historical.
        if rate_class in ("MONETARY", "NONMONETARY"):
            return closing
        if rate_class in ("REV_EXP", "REV_EXP_HIST"):
            return average
        if rate_class in EQUITY_CLASSES:
            return hist
    elif method == "temporal":
        # Remeasurement: monetary @ closing, non-monetary @ historical,
        # P&L @ average EXCEPT non-monetary-linked (REV_EXP_HIST) @ historical.
        if rate_class == "MONETARY":
            return closing
        if rate_class == "NONMONETARY":
            return hist
        if rate_class == "REV_EXP":
            return average
        if rate_class == "REV_EXP_HIST":
            return hist
        if rate_class in EQUITY_CLASSES:
            return hist
    raise SystemExit(f"no rate policy for method={method!r} rate_class={rate_class!r}")


def analytical_cta(tb: list, mapping: dict, rates: dict, net_income_func: float) -> float:
    """The ASC 830 analytical CTA the balancing plug must reconcile to.

    begin_net_assets x (closing - historical)   [computed per equity account so mixed
                                                  historical rates generalize correctly]
      + NI x (closing - average)
      - dividends x (closing - declaration)
    """
    closing, average = float(rates["closing"]), float(rates["average"])
    beg_at_closing = 0.0
    beg_at_hist = 0.0
    for r in tb:
        mp = mapping[r["account"]]
        if mp.get("rate_class") in EQUITY_CLASSES:
            pres = se._present(r, "Equity")  # functional-currency beginning net assets
            beg_at_closing += pres * closing
            beg_at_hist += pres * historical_rate(rates, r["account"])
    term_bna = beg_at_closing - beg_at_hist
    term_ni = net_income_func * (closing - average)
    div = rates.get("dividends") or {}
    div_amt = float(div.get("amount", 0) or 0)
    decl = float(div.get("declaration_rate", historical_rate(rates, "default"))) if div_amt else 0.0
    term_div = -div_amt * (closing - decl)
    return round(term_bna + term_ni + term_div, 2)


def _num(x) -> str:
    """Compact numeric string for the emitted TB (int when whole, else 2dp)."""
    x = round(float(x), 2)
    return str(int(x)) if x == int(x) else f"{x:.2f}"


def translate(entity: dict, mapping: dict, tb: list, rates: dict, presentation: str) -> dict:
    """Translate the functional TB to a presentation TB + plug; reuse statement_engine.

    Returns a dict carrying the balanced translated rows, the plug, statement_engine's
    subtotals + reasoning trail, and (current_rate) the CTA self-check.
    """
    method = rates.get("method")
    if method not in METHODS:
        raise SystemExit(f"rates.method must be one of {sorted(METHODS)}, got {method!r}")

    trail = []
    translated = []
    usd_debit_sum = usd_credit_sum = 0.0
    for r in tb:
        mp = mapping[r["account"]]
        rc = mp["rate_class"]
        rate = rate_for(method, rc, r["account"], rates)
        d = round(r["debit"] * rate, 2)
        c = round(r["credit"] * rate, 2)
        usd_debit_sum += d
        usd_credit_sum += c
        translated.append(
            {"account": r["account"], "description": r["description"], "debit": d, "credit": c}
        )
        trail.append(
            {
                "account": r["account"],
                "description": r["description"],
                "rate_class": rc,
                "rate": rate,
                "functional_debit": r["debit"],
                "functional_credit": r["credit"],
                "usd_debit": d,
                "usd_credit": c,
            }
        )

    imbalance = round(usd_debit_sum - usd_credit_sum, 2)  # +ve => debits exceed credits

    # Functional-currency net income (mapping-independent) for the analytical check.
    _, net_income_func, _ = se.build_income_statement(tb, mapping)

    work_map = {k: dict(v) for k, v in mapping.items()}
    plug = None
    if method == "current_rate":
        # Plug is the CTA, in BS/Equity. Debit-excess => a credit CTA (gain), and
        # vice-versa; either way its section-signed presentation amount == imbalance.
        d, c = (0.0, imbalance) if imbalance >= 0 else (-imbalance, 0.0)
        work_map[CTA_ACCT] = {
            "statement": "BS",
            "section": "Equity",
            "line": CTA_LINE,
            "normal_balance": "credit",
            "rate_class": "EQUITY_RE",
        }
        translated.append({"account": CTA_ACCT, "description": CTA_LINE, "debit": d, "credit": c})
        plug = {
            "type": "CTA",
            "statement": "BS",
            "section": "Equity",
            "line": CTA_LINE,
            "debit": d,
            "credit": c,
            "presentation_amount": imbalance,
        }
    else:  # temporal
        # Plug is the remeasurement gain/(loss), in IS/OtherIncomeExpense -> net income.
        d, c = (0.0, imbalance) if imbalance >= 0 else (-imbalance, 0.0)
        work_map[REMEAS_ACCT] = {
            "statement": "IS",
            "section": "OtherIncomeExpense",
            "line": REMEAS_LINE,
            "normal_balance": "credit",
            "rate_class": "REV_EXP",
        }
        translated.append(
            {"account": REMEAS_ACCT, "description": REMEAS_LINE, "debit": d, "credit": c}
        )
        plug = {
            "type": "remeasurement_gain_loss",
            "statement": "IS",
            "section": "OtherIncomeExpense",
            "line": REMEAS_LINE,
            "debit": d,
            "credit": c,
            "presentation_amount": imbalance,
        }

    # Reuse statement_engine on the balanced translated TB (no new sign logic).
    is_stmt, net_income, is_trail = se.build_income_statement(translated, work_map)
    bs_stmt, bs_trail, _ = se.build_balance_sheet(translated, work_map, net_income)

    out = {
        "entity": entity["entity_name"],
        "method": method,
        "functional_currency": entity["functional_currency"],
        "presentation_currency": presentation,
        "rates": {
            "closing": rates["closing"],
            "average": rates["average"],
            "historical": rates.get("historical"),
        },
        "plug": plug,
        "translated_income_statement": is_stmt["subtotals"],
        "translated_balance_sheet": bs_stmt["subtotals"],
        "translation_trail": trail,
        "reasoning_trail": {"income_statement": is_trail, "balance_sheet": bs_trail},
        "translated_tb": translated,
        "caveat": (
            "Decision-support translation, NOT an audited remeasurement or a "
            "GAAP/IFRS determination. Closing/average/historical rates are the "
            "consumer's sourced inputs; live-rate verification, IdP/warehouse "
            "wiring, and real credentials are out of scope."
        ),
    }

    if method == "current_rate":
        theory = analytical_cta(tb, mapping, rates, net_income_func)
        passes = abs(theory - imbalance) < 0.01
        out["cta_self_check"] = {"analytical": theory, "plug": imbalance, "passes": passes}
        if not passes:
            sys.stderr.write(
                f"BLOCKED: CTA self-check failed - balancing plug {imbalance:,.2f} != "
                f"analytical CTA {theory:,.2f} (begin_net_assets x (closing-historical) "
                f"+ NI x (closing-average) - dividends x (closing-declaration)).\n"
            )
            raise SystemExit(RC_CTA_SELFCHECK)
    return out


def run(entity_path: str, coa_path: str, tb_path: str, rates_path=None, presentation="USD") -> dict:
    profile = ec.load(entity_path)
    perrs = ec.validate(profile)
    if perrs:
        sys.stderr.write(f"BLOCKED: invalid entity profile {entity_path}:\n")
        for e in perrs:
            sys.stderr.write(f"  - {e}\n")
        raise SystemExit(RC_ENTITY)

    tb = se.load_tb(tb_path)
    tb_debits = round(sum(r["debit"] for r in tb), 2)
    tb_credits = round(sum(r["credit"] for r in tb), 2)
    if abs(tb_debits - tb_credits) >= 0.01:
        sys.stderr.write(
            f"BLOCKED: functional trial balance is out of balance by "
            f"{tb_debits - tb_credits:,.2f} (debits {tb_debits:,.2f} != credits "
            f"{tb_credits:,.2f}). Translate only a balanced TB.\n"
        )
        raise SystemExit(RC_TB_UNBALANCED)

    functional = profile["functional_currency"]
    if functional == presentation:
        # Zero-drift no-op: nothing to translate. Signalled to the caller so main() can
        # emit a byte-identical copy of the source TB.
        return {
            "entity": profile["entity_name"],
            "method": None,
            "functional_currency": functional,
            "presentation_currency": presentation,
            "no_op": True,
            "caveat": (
                "functional == presentation currency: no translation "
                "performed; the presentation TB is a byte-identical copy."
            ),
        }

    mapping = load_mapping_with_rate_class(coa_path)
    errs = se.lint_mapping(tb, mapping) + lint_rate_class(tb, mapping)
    if errs:
        sys.stderr.write("BLOCKED: mapping / rate_class errors:\n")
        for e in errs:
            sys.stderr.write(f"  - {e}\n")
        raise SystemExit(RC_MAPPING)

    if rates_path is None:
        raise SystemExit(
            "BLOCKED: --rates is required when functional currency "
            f"({functional}) != presentation currency ({presentation})."
        )
    with open(rates_path) as fh:
        rates = json.load(fh)

    method = rates.get("method")
    if method not in METHODS:
        raise SystemExit(f"BLOCKED: rates.method must be one of {sorted(METHODS)}, got {method!r}")

    # Validate the required numeric rate keys up front so a missing/blank key BLOCKS with a
    # worded message + dedicated RC code, rather than surfacing later as a raw KeyError inside
    # rate_for()'s float(rates['closing'])/float(rates['average']). Both methods translate at
    # closing/average and at historical (equity/non-monetary), so historical.default is always
    # needed here — mirror historical_rate()'s own check.
    rate_errs: list = []
    for key in ("closing", "average"):
        if key not in rates:
            rate_errs.append(f"rates.{key} is required (a numeric FX rate)")
        else:
            try:
                float(rates[key])
            except (TypeError, ValueError):
                rate_errs.append(f"rates.{key} must be numeric, got {rates[key]!r}")
    hist = rates.get("historical")
    if not isinstance(hist, dict) or "default" not in hist:
        rate_errs.append(
            "rates.historical must be an object with a 'default' key "
            "(and optional per-account overrides)"
        )
    if rate_errs:
        sys.stderr.write("BLOCKED: rates.json is missing/invalid a required rate key:\n")
        for e in rate_errs:
            sys.stderr.write(f"  - {e}\n")
        raise SystemExit(RC_RATES)

    if rates.get("highly_inflationary") and method == "current_rate":
        sys.stderr.write(
            "REFUSED: highly_inflationary + current_rate is not permitted. Under ASC "
            "830 a highly inflationary economy's books are REMEASURED as if the "
            "reporting currency were functional (use method='temporal'), never "
            "translated at the current rate. IAS 29 (restate-for-inflation-then-"
            "translate at closing) is a different framework and is OUT OF SCOPE here.\n"
        )
        raise SystemExit(RC_HYPERINFLATION)

    return translate(profile, mapping, tb, rates, presentation)


def _write_tb_csv(path: str, entity: dict, rows: list, presentation: str) -> None:
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["account", "description", "debit", "credit", "entity", "period", "currency"])
        for r in rows:
            w.writerow(
                [
                    r["account"],
                    r["description"],
                    _num(r["debit"]),
                    _num(r["credit"]),
                    entity.get("entity_name", ""),
                    entity.get("fiscal_period", ""),
                    presentation,
                ]
            )


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Translate/remeasure one entity's functional-currency TB to a "
        "presentation-currency TB (current-rate or temporal)."
    )
    p.add_argument("--entity", required=True, help="entity profile JSON")
    p.add_argument("--coa", required=True, help="COA mapping CSV (with rate_class)")
    p.add_argument("--tb", required=True, help="functional-currency trial balance CSV")
    p.add_argument("--rates", help="rates.json (required when functional != presentation)")
    p.add_argument(
        "--presentation-currency", default="USD", help="group presentation currency (default USD)"
    )
    p.add_argument("--out", help="write the translation report JSON here (else stdout)")
    p.add_argument("--out-tb", help="write the presentation-currency TB CSV here")
    a = p.parse_args(argv)

    out = run(a.entity, a.coa, a.tb, a.rates, a.presentation_currency)

    if out.get("no_op"):
        # Byte-identical copy of the source TB (zero-drift guarantee).
        if a.out_tb:
            with open(a.tb, "rb") as src, open(a.out_tb, "wb") as dst:
                dst.write(src.read())
        text = json.dumps(out, indent=2)
        if a.out:
            with open(a.out, "w") as fh:
                fh.write(text + "\n")
            print(
                f"no-op (functional == {a.presentation_currency}); presentation TB is "
                f"a byte-identical copy" + (f" -> {a.out_tb}" if a.out_tb else "")
            )
        else:
            print(text)
        return 0

    if a.out_tb:
        profile = ec.load(a.entity)
        _write_tb_csv(a.out_tb, profile, out["translated_tb"], a.presentation_currency)

    text = json.dumps(out, indent=2)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text + "\n")
        plug = out["plug"]
        ni = out["translated_balance_sheet"]["current_period_net_income"]
        delta = out["translated_balance_sheet"]["balance_delta"]
        print(
            f"wrote {a.out}  [{out['method']}]  {plug['type']} "
            f"{plug['presentation_amount']:,.2f}  net income {ni:,.2f} "
            f"{a.presentation_currency}  balance_delta {delta:,.2f}"
        )
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
