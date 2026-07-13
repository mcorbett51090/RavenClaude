#!/usr/bin/env python3
"""schedule_engine.py - standard close schedules (depreciation / prepaid / deferred-revenue).

The recurring supporting schedules a controller re-derives every close and staples
behind the balance sheet as tie-out evidence. Producing them is a COMMODITY (a fixed-
asset sub-ledger, an ERP amortization module, or a spreadsheet already does it) — this
engine earns its place the same way the rest of the controller-autopilot does: it is
*self-checking and blocking*, so a schedule can sit inside the governed close
(close_state.py) as evidence rather than as an unverified attachment. Two disciplines:

  1. EVERY SCHEDULE MUST TIE. Each subcommand is a rollforward whose identity is
     beginning + movements == ending (asset by asset AND in total). The engine computes
     the residual and refuses (--strict) to emit a schedule whose portfolio rollforward
     does not tie to the cent. A schedule that does not tie is not evidence — it is a
     plug wearing a schedule's clothes.

  2. STRAIGHT-LINE, DISCLOSED. All three schedules use the simplest defensible method —
     straight-line depreciation, straight-line prepaid amortization, ratable revenue
     recognition — with a final-period catch-up so the balance lands EXACTLY at its
     floor (salvage for an asset, zero for a prepaid / a fully-recognized contract). The
     method is stated on the artifact; anything a real close needs beyond straight-line
     (accelerated/MACRS tax depreciation, usage-based recognition, ASC 606 variable
     consideration) is OUT of scope and must be modeled explicitly, not assumed here.

PRESENTATION SIGN reuses the statement_engine.py convention: a schedule's amounts carry
the sign of the STATEMENT SECTION the schedule ties into, not an account's normal
balance. Gross fixed assets and prepaids live in an asset section (debit-positive), so
they are carried as positive magnitudes; ACCUMULATED DEPRECIATION is a contra-asset
(credit-natural) presented as a positive number that REDUCES net book value within the
asset section — exactly how a contra reduces its section in statement_engine._present().
Deferred revenue ties into a liability section (credit-positive). The rollforwards below
present each balance as a positive magnitude with movements signed by direction, which
is the standard schedule shape and consistent with that section-driven sign rule.

Fixtures are SYNTHETIC and obviously fake. Outputs are decision-support, not an
accounting / audit / tax opinion (../CLAUDE.md sec.3). A schedule derived from a
summarized input file is not a substitute for a fixed-asset sub-ledger reconciled to
the GL, nor for a tax-basis depreciation calc. Stdlib only (csv/json/argparse). 3.8+.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys

DISCLAIMER = (
    "Straight-line close schedule from summarized inputs; decision-support, "
    "NOT an audit/tax opinion or a sub-ledger reconciled to the GL."
)


# ---- period arithmetic (YYYY-MM as an absolute month index) ----------------
def _ym(s: str) -> int:
    """'YYYY-MM' -> absolute month index (year*12 + month0). Blocks a malformed period."""
    try:
        y, m = s.strip().split("-")
        yi, mi = int(y), int(m)
        if not (1 <= mi <= 12):
            raise ValueError
        return yi * 12 + (mi - 1)
    except (ValueError, AttributeError):
        raise SystemExit(f"bad period {s!r}: expected YYYY-MM (e.g. 2026-06)")


def _ym_str(n: int) -> str:
    return f"{n // 12:04d}-{n % 12 + 1:02d}"


def _read_csv(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def _num(row: dict, key: str, default: float = 0.0) -> float:
    raw = (row.get(key) or "").strip()
    if raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        raise SystemExit(
            f"non-numeric {key}={raw!r} for {row.get('asset_id') or row.get('prepaid_id') or row.get('contract_id') or '?'}"
        )


def _tie(beginning: float, additions: float, reductions: float, ending: float) -> dict:
    """Rollforward identity: beginning + additions - reductions - ending should be 0.00."""
    residual = round(beginning + additions - reductions - ending, 2)
    return {
        "beginning": round(beginning, 2),
        "additions": round(additions, 2),
        "reductions": round(reductions, 2),
        "ending": round(ending, 2),
        "residual": residual,
        "ties": abs(residual) < 0.005,
    }


# ---- depreciation: fixed-asset rollforward ---------------------------------
def depreciation(rows: list[dict], period: str) -> dict:
    """Straight-line fixed-asset rollforward for one period.

    Full-month convention: an asset depreciates in the month it is placed in service and
    NOT in the month it is disposed (disposed at start of period). Three parallel
    rollforwards tie: gross cost, accumulated depreciation, and net book value (NBV),
    with NBV = gross cost - accumulated depreciation at both beginning and ending.
    """
    p = _ym(period)
    assets, skipped = [], []
    for r in rows:
        aid = (r.get("asset_id") or "").strip()
        cost = _num(r, "cost")
        salvage = _num(r, "salvage_value")
        life = int(float((r.get("useful_life_months") or "0").strip() or 0))
        if life <= 0:
            raise SystemExit(f"{aid}: useful_life_months must be > 0")
        iserv = _ym((r.get("in_service_month") or "").strip())
        disp_raw = (r.get("disposal_month") or "").strip()
        dmon = _ym(disp_raw) if disp_raw else None

        base = round(cost - salvage, 2)  # depreciable base
        monthly = round(base / life, 2)
        e = p - iserv  # full months since in service
        if e < 0:
            skipped.append({"asset_id": aid, "reason": "placed in service after period"})
            continue
        if dmon is not None and dmon < p:
            skipped.append({"asset_id": aid, "reason": "disposed before period"})
            continue

        on_books_start = e >= 1
        b_cost = round(cost, 2) if on_books_start else 0.0
        months_before = min(e, life) if on_books_start else 0
        # Beginning accumulated depreciation. Once the asset has been on the books for
        # its full life it is FULLY depreciated -> accum is EXACTLY the depreciable base
        # (cost - salvage). Deriving it from months_before*monthly would strand the
        # monthly rounding remainder (base - life*monthly > 0 when monthly rounds down),
        # so a period AFTER the final month would re-open with NBV above salvage
        # (2026-07-13 review). Anchoring to base keeps ending(N) == beginning(N+1).
        if months_before >= life:
            b_accum = base
        else:
            b_accum = round(min(round(months_before * monthly, 2), base), 2)
        b_nbv = round(b_cost - b_accum, 2)

        addition = round(cost, 2) if e == 0 else 0.0
        disposed_here = dmon is not None and dmon == p
        if disposed_here or e >= life:
            dep = 0.0  # fully depreciated, or disposed this period
        elif e == life - 1:
            # Final depreciation month: drain the FULL remaining base so ending accum
            # lands EXACTLY at base and NBV at salvage regardless of rounding direction
            # (mirrors _ratable_item / _full_schedule's final-period catch-up). The prior
            # min(monthly, base - b_accum) left a residual when monthly rounded down.
            dep = round(base - b_accum, 2)
        else:
            dep = round(min(monthly, base - b_accum), 2)
        disp_cost = round(cost, 2) if disposed_here else 0.0
        disp_accum = b_accum if disposed_here else 0.0
        disp_nbv = round(disp_cost - disp_accum, 2)

        e_cost = round(b_cost + addition - disp_cost, 2)
        e_accum = round(b_accum + dep - disp_accum, 2)
        e_nbv = round(e_cost - e_accum, 2)
        proceeds = _num(r, "disposal_proceeds") if disposed_here else 0.0
        gain_loss = round(proceeds - disp_nbv, 2) if disposed_here else None

        assets.append(
            {
                "asset_id": aid,
                "description": (r.get("description") or "").strip(),
                "cost": round(cost, 2),
                "salvage_value": round(salvage, 2),
                "useful_life_months": life,
                "monthly_depreciation": monthly,
                "in_service_month": _ym_str(iserv),
                "beginning_cost": b_cost,
                "beginning_accum_depreciation": b_accum,
                "beginning_nbv": b_nbv,
                "additions": addition,
                "depreciation": dep,
                "disposal_cost": disp_cost,
                "disposal_accum_depreciation": disp_accum,
                "disposal_nbv": disp_nbv,
                "disposal_proceeds": round(proceeds, 2) if disposed_here else None,
                "gain_loss_on_disposal": gain_loss,
                "ending_cost": e_cost,
                "ending_accum_depreciation": e_accum,
                "ending_nbv": e_nbv,
                "nbv_tie_ok": abs((b_nbv + addition - dep - disp_nbv) - e_nbv) < 0.005,
            }
        )

    def col(k):
        return round(sum(a[k] for a in assets), 2)

    cost_rf = _tie(
        col("beginning_cost"), col("additions"), col("disposal_cost"), col("ending_cost")
    )
    accum_rf = _tie(
        col("beginning_accum_depreciation"),
        col("depreciation"),
        col("disposal_accum_depreciation"),
        col("ending_accum_depreciation"),
    )
    nbv_rf = _tie(
        col("beginning_nbv"),
        col("additions"),
        round(col("depreciation") + col("disposal_nbv"), 2),
        col("ending_nbv"),
    )
    cross_tie = (
        abs(col("ending_cost") - col("ending_accum_depreciation") - col("ending_nbv")) < 0.005
    )
    return {
        "schedule": "depreciation",
        "period": period,
        "method": "straight-line, full-month convention",
        "disclaimer": DISCLAIMER,
        "assets": assets,
        "skipped": skipped,
        "rollforward": {
            "gross_cost": cost_rf,
            "accumulated_depreciation": accum_rf,
            "net_book_value": nbv_rf,
            "nbv_equals_cost_less_accum": cross_tie,
        },
        "formula": (
            "ending NBV = beginning NBV + additions - depreciation - disposals(NBV); "
            "ending accum = beginning accum + depreciation - accum removed on disposal; "
            "NBV = gross cost - accumulated depreciation"
        ),
        "ties": cost_rf["ties"] and accum_rf["ties"] and nbv_rf["ties"] and cross_tie,
    }


# ---- ratable balance rollforward (shared by prepaid + deferred revenue) -----
def _ratable_item(total: float, term: int, start: str, period: str) -> tuple:
    """One straight-line/ratable balance's (opening, addition, drawdown, ending, monthly)
    for a single reporting period. Addition lands in the start month; drawdown is the
    ratable slice with a final-period catch-up so the balance drains exactly to zero."""
    if term <= 0:
        raise SystemExit(f"term_months must be > 0 (got {term})")
    monthly = round(total / term, 2)
    s, p = _ym(start), _ym(period)
    k = p - s  # 0-based month index within the term
    if k <= 0:
        opening = 0.0
    elif k >= term:
        # Past the term the item is fully drained (the k == term-1 period already
        # took the full remaining balance), so it re-opens at exactly zero. Deriving
        # opening from total - term*monthly would strand the rounding remainder
        # (total - term*monthly > 0 when monthly rounds down) as a phantom balance
        # that never clears (2026-07-13 review).
        opening = 0.0
    else:
        drawn_before = round(min(k, term) * monthly, 2)
        opening = round(total - min(drawn_before, round(total, 2)), 2)
    addition = round(total, 2) if k == 0 else 0.0
    if k == term - 1:
        # Final period drains the balance to exactly zero (mirrors _full_schedule's
        # last row): take the full remaining balance, not the ratable slice, so a
        # rounds-down monthly can't leave total - term*monthly on the books.
        drawdown = round(opening + addition, 2)
    elif 0 <= k < term - 1:
        drawn_before = round(min(k, term) * monthly, 2)
        drawdown = round(min(monthly, round(total, 2) - drawn_before), 2)
    else:
        drawdown = 0.0
    ending = round(opening + addition - drawdown, 2)
    return opening, addition, drawdown, ending, monthly


def _full_schedule(total: float, term: int, start: str) -> list[dict]:
    """Whole-term month-by-month waterfall; final month drains the balance to exactly 0."""
    monthly = round(total / term, 2)
    rows, bal = [], 0.0
    for i in range(term):
        opening = round(bal, 2)
        addition = round(total, 2) if i == 0 else 0.0
        avail = round(opening + addition, 2)
        drawdown = round(min(monthly, avail), 2) if i < term - 1 else round(avail, 2)
        closing = round(avail - drawdown, 2)
        rows.append(
            {
                "period": _ym_str(_ym(start) + i),
                "opening": opening,
                "addition": addition,
                "drawdown": drawdown,
                "closing": closing,
            }
        )
        bal = closing
    return rows


def _ratable_schedule(rows, period, id_key, add_label, draw_label, kind, title):
    """Generic ratable rollforward used by prepaid and deferred-revenue."""
    items, port_open, port_add, port_draw, port_end = [], 0.0, 0.0, 0.0, 0.0
    for r in rows:
        iid = (r.get(id_key) or "").strip()
        total = _num(r, "total_amount" if id_key == "prepaid_id" else "billing_amount")
        term = int(float((r.get("term_months") or "0").strip() or 0))
        start = (r.get("start_month") or "").strip()
        opening, addition, drawdown, ending, monthly = _ratable_item(total, term, start, period)
        port_open += opening
        port_add += addition
        port_draw += drawdown
        port_end += ending
        items.append(
            {
                id_key: iid,
                "description": (r.get("description") or "").strip(),
                "total_amount": round(total, 2),
                "term_months": term,
                "start_month": start,
                "monthly_amount": monthly,
                "opening_balance": opening,
                add_label: addition,
                draw_label: drawdown,
                "ending_balance": ending,
                "tie_ok": abs((opening + addition - drawdown) - ending) < 0.005,
                "full_schedule": _full_schedule(total, term, start),
            }
        )
    rf = _tie(port_open, port_add, port_draw, port_end)
    return {
        "schedule": kind,
        "period": period,
        "method": "straight-line ratable, final-period catch-up",
        "disclaimer": DISCLAIMER,
        "title": title,
        "items": items,
        "rollforward": rf,
        "formula": f"ending {kind} = opening + {add_label} - {draw_label}",
        "ties": rf["ties"] and all(i["tie_ok"] for i in items),
    }


def prepaid(rows: list[dict], period: str) -> dict:
    return _ratable_schedule(
        rows,
        period,
        "prepaid_id",
        "additions",
        "amortization",
        "prepaid",
        "Prepaid expense amortization schedule",
    )


def deferred_revenue(rows: list[dict], period: str) -> dict:
    return _ratable_schedule(
        rows,
        period,
        "contract_id",
        "billings",
        "recognized",
        "deferred-revenue",
        "Deferred revenue waterfall",
    )


# ---- CLI -------------------------------------------------------------------
def _emit(result: dict, out: str | None, strict: bool) -> int:
    if strict and not result["ties"]:
        sys.stderr.write(
            f"BLOCKED (--strict): {result['schedule']} schedule does not tie "
            f"(beginning + movements != ending). Residual(s) present.\n"
        )
        return 5
    text = json.dumps(result, indent=2)
    if out:
        with open(out, "w") as fh:
            fh.write(text + "\n")
        print(f"wrote {out}  [{result['schedule']}]  ties={result['ties']}")
    else:
        print(text)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Standard close schedules (depreciation / prepaid / deferred-revenue)."
    )
    p.add_argument(
        "--strict", action="store_true", help="exit non-zero if the rollforward does not tie"
    )
    p.add_argument("--out", help="write schedule JSON here (else stdout)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("depreciation", help="fixed-asset rollforward (straight-line)")
    s.add_argument("--assets", required=True, help="fixed-asset CSV")
    s.add_argument("--period", required=True, help="reporting period YYYY-MM")

    s = sub.add_parser("prepaid", help="prepaid amortization schedule")
    s.add_argument("--prepaids", required=True, help="prepaid items CSV")
    s.add_argument("--period", required=True, help="reporting period YYYY-MM")

    s = sub.add_parser("deferred-revenue", help="deferred revenue waterfall")
    s.add_argument("--contracts", required=True, help="deferred-revenue contracts CSV")
    s.add_argument("--period", required=True, help="reporting period YYYY-MM")

    a = p.parse_args(argv)
    if a.cmd == "depreciation":
        result = depreciation(_read_csv(a.assets), a.period)
    elif a.cmd == "prepaid":
        result = prepaid(_read_csv(a.prepaids), a.period)
    elif a.cmd == "deferred-revenue":
        result = deferred_revenue(_read_csv(a.contracts), a.period)
    else:  # pragma: no cover - argparse enforces
        p.error(f"unknown command {a.cmd!r}")
    return _emit(result, a.out, a.strict)


if __name__ == "__main__":
    raise SystemExit(main())
