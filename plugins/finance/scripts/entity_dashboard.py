#!/usr/bin/env python3
"""entity_dashboard.py - a productized, per-entity close dashboard from a close package.

WHAT THIS IS (and is NOT). This renders the close package that controller_cycle.py
already produced (`--out-json`) into a single, self-contained, per-entity dashboard
HTML a controller or a reviewer opens offline: headline KPIs, the IS/BS summaries,
the reconciliation exceptions, the top flux movements, and the governance state +
traceability / self-certified badges. It reads ONLY the committed package JSON — it
recomputes no statement math beyond a handful of ratio derivations, so a number that
was blocked, badged, or materiality-suppressed upstream stays that way here. The
dashboard is a *presentation surface*, not a second source of truth.

  1. KPIs ARE DERIVED, NOT ASSERTED. Revenue / net income / gross margin come straight
     from the income-statement subtotals. Current ratio needs current liabilities,
     which the balance-sheet SUBTOTALS do not carry, so it is recomputed from the
     statement reasoning trail's `CurrentLiabilities` section (presentation-signed,
     the same convention statement_engine.py uses so contra-accounts stay correct) —
     and if the trail is absent, the KPI is shown "n/a", never plugged. DSO is an
     honest single-period proxy: AR (the balance-sheet line whose name carries
     "receivable") over the period's own revenue times the period's own day count,
     labeled as such — not annualized behind the reader's back.

  2. IT INHERITS UPSTREAM HONESTY, IT DOES NOT MANUFACTURE IT. The traceability badge
     (TB-only vs GL-detail-traced), the "unaudited draft" cash-flow label, and the
     "self-certified / single-actor" governance caveat are carried through verbatim
     from the package. A green KPI on a self-certified package is still a self-
     certified package, and the banner says so.

  3. SELF-CONTAINED + CSP-SAFE. Inline CSS/JS only, zero external requests (no CDN
     font, no remote image, no fetch) so it opens from disk and is safe to email to a
     reviewer. Light + dark via prefers-color-scheme with a data-theme override.
     tabular-nums so columns of figures line up.

MULTI-TENANT / RECURRING-DELIVERY NOTE. This is the SINGLE-ENTITY, file-in / file-out
tier. The recurring, warehouse-backed, multi-tenant version (many entities, row-level
isolation, an embedded live dashboard) is NOT this file's job and is deliberately not
reimplemented here: it reuses data-platform's row-level-security and signed-JWT embed
work (skills `rls-policy-authoring` / `jwt-embed-issuance`). Auth, tenant isolation,
and token issuance are that plugin's owned surface — do not hand-roll them here.

Outputs are decision-support, not an accounting/audit/tax opinion (../CLAUDE.md sec.3).
Stdlib only (json/argparse/html/datetime). Python 3.8+.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import date


def _money(n, dash="—"):
    if n is None:
        return dash
    return f"{n:,.2f}"


def _pct(n, dash="n/a"):
    if n is None:
        return dash
    return f"{n:,.1f}%"


def _ratio(n, dash="n/a"):
    if n is None:
        return dash
    return f"{n:,.2f}×"


def _days(n, dash="n/a"):
    if n is None:
        return dash
    return f"{n:,.1f} days"


def _days_in_period(period: str):
    """Day count for a 'YYYY-MM' period, else None (DSO then shows n/a, never plugged)."""
    try:
        parts = str(period).split("-")
        y, m = int(parts[0]), int(parts[1])
        if not (1 <= m <= 12):
            return None
        nxt = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
        return (nxt - date(y, m, 1)).days
    except (ValueError, IndexError, TypeError):
        return None


def _current_liabilities(statements: dict):
    """Sum the CurrentLiabilities section from the BS reasoning trail (presentation-signed).

    The BS subtotals expose total_liabilities but NOT current vs non-current, so the
    current-ratio denominator is recovered from the trail. Absent the trail -> None,
    and the current ratio is shown 'n/a' rather than guessed.
    """
    trail = ((statements.get("reasoning_trail") or {}).get("balance_sheet")) or []
    if not trail:
        return None
    total = 0.0
    seen = False
    for row in trail:
        if row.get("section") == "CurrentLiabilities":
            seen = True
            total += float(row.get("amount") or 0.0)
    return round(total, 2) if seen else None


def _receivables(statements: dict):
    """The balance-sheet line whose name carries 'receivable' (for DSO). None if absent."""
    lines = (statements.get("balance_sheet") or {}).get("lines") or {}
    for name, amount in lines.items():
        if "receivable" in name.lower():
            return float(amount)
    return None


def derive_kpis(pkg: dict) -> dict:
    """Headline KPIs, each either derived from the package or explicitly None ('n/a')."""
    st = pkg.get("statements") or {}
    iss = (st.get("income_statement") or {}).get("subtotals") or {}
    bss = (st.get("balance_sheet") or {}).get("subtotals") or {}

    revenue = iss.get("revenue")
    net_income = iss.get("net_income")
    gross_profit = iss.get("gross_profit")

    gross_margin = (round(gross_profit / revenue * 100, 1)
                    if revenue not in (None, 0) and gross_profit is not None else None)
    net_margin = (round(net_income / revenue * 100, 1)
                  if revenue not in (None, 0) and net_income is not None else None)

    cur_assets = bss.get("total_current_assets")
    cur_liab = _current_liabilities(st)
    current_ratio = (round(cur_assets / cur_liab, 2)
                     if cur_assets is not None and cur_liab not in (None, 0) else None)

    ar = _receivables(st)
    days = _days_in_period(pkg.get("period", ""))
    dso = (round(ar / revenue * days, 1)
           if ar is not None and revenue not in (None, 0) and days else None)

    return {
        "revenue": revenue,
        "net_income": net_income,
        "gross_margin_pct": gross_margin,
        "net_margin_pct": net_margin,
        "current_ratio": current_ratio,
        "current_assets": cur_assets,
        "current_liabilities": cur_liab,
        "dso_days": dso,
        "dso_days_basis": days,
    }


# ---- rendering -----------------------------------------------------------

_STYLE = """
  :root { --bg:#fff; --fg:#1a2233; --muted:#5b6472; --line:#e4e8f0; --accent:#1f6feb;
          --ok:#137333; --warn:#9a6700; --flag:#b3261e; --card:#f7f9fc; --kpi:#eef3fb; }
  @media (prefers-color-scheme: dark) { :root { --bg:#0d1117; --fg:#e6edf3; --muted:#9aa4b2;
          --line:#232a35; --accent:#4d9fff; --ok:#3fb950; --warn:#d29922; --flag:#f85149;
          --card:#161b22; --kpi:#12181f; } }
  :root[data-theme="light"] { --bg:#fff; --fg:#1a2233; --muted:#5b6472; --line:#e4e8f0;
          --accent:#1f6feb; --ok:#137333; --warn:#9a6700; --flag:#b3261e; --card:#f7f9fc; --kpi:#eef3fb; }
  :root[data-theme="dark"] { --bg:#0d1117; --fg:#e6edf3; --muted:#9aa4b2; --line:#232a35;
          --accent:#4d9fff; --ok:#3fb950; --warn:#d29922; --flag:#f85149; --card:#161b22; --kpi:#12181f; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--fg);
         font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
  .wrap { max-width:1000px; margin:0 auto; padding:28px 20px 64px; }
  header { border-bottom:2px solid var(--line); padding-bottom:16px; margin-bottom:8px; }
  h1 { font-size:25px; margin:0 0 4px; } h2 { font-size:18px; margin:30px 0 10px; }
  .sub { color:var(--muted); font-size:14px; }
  .pills { margin-top:10px; display:flex; gap:8px; flex-wrap:wrap; }
  .pill { font-size:12px; font-weight:600; padding:3px 9px; border-radius:20px; border:1px solid var(--line); }
  .pill.ok { color:var(--ok); border-color:var(--ok); }
  .pill.warn { color:var(--warn); border-color:var(--warn); }
  .banner { margin:14px 0; padding:10px 14px; border-radius:8px; font-size:13px;
            background:color-mix(in srgb, var(--warn) 12%, transparent); border:1px solid var(--warn); color:var(--warn); }
  .note { margin:14px 0; padding:10px 14px; border-radius:8px; font-size:12.5px;
          background:var(--card); border:1px solid var(--line); color:var(--muted); }
  .kpis { display:grid; grid-template-columns:repeat(auto-fit,minmax(160px,1fr)); gap:12px; margin-top:16px; }
  .kpi { background:var(--kpi); border:1px solid var(--line); border-radius:12px; padding:14px 16px; }
  .kpi .label { color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }
  .kpi .value { font-size:26px; font-weight:700; margin-top:4px; font-variant-numeric:tabular-nums; }
  .kpi .foot { color:var(--muted); font-size:12px; margin-top:2px; }
  .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
  @media (max-width:720px) { .grid2 { grid-template-columns:1fr; } }
  table { width:100%; border-collapse:collapse; margin:6px 0 4px; font-size:14px; }
  .tablewrap { overflow-x:auto; }
  th,td { text-align:left; padding:7px 10px; border-bottom:1px solid var(--line); }
  th { color:var(--muted); font-weight:600; font-size:12px; text-transform:uppercase; letter-spacing:.04em; }
  td.num, th.num { text-align:right; font-variant-numeric:tabular-nums; }
  tr.subtotal td { font-weight:700; border-top:2px solid var(--line); }
  tr.flag { background:color-mix(in srgb, var(--flag) 10%, transparent); }
  .card { background:var(--card); border:1px solid var(--line); border-radius:10px; padding:4px 14px; }
  .status { font-weight:700; font-size:12px; }
  .s-pass { color:var(--ok); } .s-flag { color:var(--flag); } .s-selfsupported { color:var(--muted); }
  .muted { color:var(--muted); }
  .caveat { color:var(--warn); font-size:13px; }
  code { background:color-mix(in srgb, var(--fg) 8%, transparent); padding:1px 5px; border-radius:4px; font-size:13px; }
  .toggle { float:right; cursor:pointer; font-size:12px; color:var(--accent);
            border:1px solid var(--line); border-radius:6px; padding:3px 8px; background:none; }
"""

_SCRIPT = """
  (function () {
    var btn = document.getElementById('themeToggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var r = document.documentElement;
      r.setAttribute('data-theme', r.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    });
  })();
"""


def _kpi_card(label, value, foot=""):
    foot_html = f"<div class='foot'>{html.escape(foot)}</div>" if foot else ""
    return (f"<div class='kpi'><div class='label'>{html.escape(label)}</div>"
            f"<div class='value'>{value}</div>{foot_html}</div>")


def render_dashboard(pkg: dict) -> str:
    ent = html.escape(str(pkg.get("entity", "Entity")))
    period = html.escape(str(pkg.get("period", "")))
    cur = html.escape(str(pkg.get("currency", "")))
    st = pkg.get("statements") or {}
    iss = (st.get("income_statement") or {}).get("subtotals") or {}
    bss = (st.get("balance_sheet") or {}).get("subtotals") or {}
    badge = html.escape(str(st.get("traceability_badge", "unknown")))
    badge_class = "ok" if "traced" in badge else "warn"
    state = pkg.get("workflow_state") or {}
    state_name = html.escape(str(state.get("state", "draft")))
    self_cert = state.get("self_certified")
    kpi = derive_kpis(pkg)

    # KPI cards
    net_margin_foot = ("net margin " + _pct(kpi["net_margin_pct"])
                       if kpi["net_margin_pct"] is not None else "net margin n/a")
    cr_foot = (f"CA {_money(kpi['current_assets'])} / CL {_money(kpi['current_liabilities'])}"
               if kpi["current_ratio"] is not None
               else "needs current-liability detail (statement trail)")
    dso_foot = (f"AR ÷ period revenue × {kpi['dso_days_basis']}d (single-period proxy)"
                if kpi["dso_days"] is not None else "AR line / period days not derivable")
    kpis_html = "".join([
        _kpi_card(f"Revenue ({cur})", _money(kpi["revenue"]), f"period {period}"),
        _kpi_card(f"Net income ({cur})", _money(kpi["net_income"]), net_margin_foot),
        _kpi_card("Gross margin", _pct(kpi["gross_margin_pct"]), "gross profit / revenue"),
        _kpi_card("Current ratio", _ratio(kpi["current_ratio"]), cr_foot),
        _kpi_card("DSO", _days(kpi["dso_days"]), dso_foot),
    ])

    # Governance banner (inherits upstream honesty)
    cert_banner = ""
    if self_cert is not False:
        cert_banner = ("<div class='banner'>SELF-CERTIFIED / SINGLE-ACTOR — identity is "
                       "config-asserted, not authenticated. This dashboard presents an "
                       "un-locked package; it is not audit-grade until locked with a non-agent "
                       "approval token at the warehouse / IdP tier.</div>")

    # Income statement summary
    is_rows = "".join([
        f"<tr><td>Revenue</td><td class='num'>{_money(iss.get('revenue'))}</td></tr>",
        f"<tr><td>Cost of goods sold</td><td class='num'>{_money(iss.get('cogs'))}</td></tr>",
        f"<tr class='subtotal'><td>Gross profit</td><td class='num'>{_money(iss.get('gross_profit'))}</td></tr>",
        f"<tr><td>Operating expenses</td><td class='num'>{_money(iss.get('operating_expenses'))}</td></tr>",
        f"<tr class='subtotal'><td>Operating income</td><td class='num'>{_money(iss.get('operating_income'))}</td></tr>",
        f"<tr><td>Other income / (expense), net</td><td class='num'>{_money(iss.get('other_income_expense_net'))}</td></tr>",
        f"<tr><td>Income tax expense</td><td class='num'>{_money(iss.get('income_tax_expense'))}</td></tr>",
        f"<tr class='subtotal'><td>Net income</td><td class='num'>{_money(iss.get('net_income'))}</td></tr>",
    ])

    # Balance sheet summary
    bs_rows = "".join([
        f"<tr><td>Total current assets</td><td class='num'>{_money(bss.get('total_current_assets'))}</td></tr>",
        f"<tr class='subtotal'><td>Total assets</td><td class='num'>{_money(bss.get('total_assets'))}</td></tr>",
        f"<tr><td>Total liabilities</td><td class='num'>{_money(bss.get('total_liabilities'))}</td></tr>",
        f"<tr><td>Equity, beginning</td><td class='num'>{_money(bss.get('equity_beginning'))}</td></tr>",
        f"<tr><td>Current-period net income</td><td class='num'>{_money(bss.get('current_period_net_income'))}</td></tr>",
        f"<tr class='subtotal'><td>Total equity</td><td class='num'>{_money(bss.get('total_equity'))}</td></tr>",
        f"<tr><td>Balance check (A − L − E)</td><td class='num'>{_money(bss.get('balance_delta'))}</td></tr>",
    ])

    # Reconciliation exceptions (FLAG rows first, then a count of the rest)
    recon = pkg.get("reconciliation") or {}
    accounts = recon.get("accounts") or []
    flagged = [r for r in accounts if r.get("status") == "FLAG"]
    if flagged:
        recon_rows = "".join(
            f"<tr class='flag'><td>{html.escape(str(r.get('account', '')))}</td>"
            f"<td>{html.escape(str(r.get('description', '')))}</td>"
            f"<td class='num'>{_money(r.get('book_balance'))}</td>"
            f"<td class='num'>{_money(r.get('subledger_balance'))}</td>"
            f"<td class='num'>{_money(r.get('difference'))}</td>"
            f"<td class='status s-flag'>{html.escape(str(r.get('status', '')))}</td></tr>"
            for r in flagged
        )
    else:
        recon_rows = ("<tr><td colspan='6' class='muted'>No reconciliation breaks at or above "
                      "materiality — all tied accounts pass review-by-exception.</td></tr>")
    n_pass = sum(1 for r in accounts if r.get("status") == "PASS")
    n_self = sum(1 for r in accounts if r.get("status") == "self-supported")

    # Top flux movements
    flux = pkg.get("flux") or {"material_movements": []}
    movements = flux.get("material_movements") or []
    top = movements[:8]
    if top:
        flux_rows = "".join(
            f"<tr><td>{html.escape(str(m.get('account', '')))}</td>"
            f"<td>{html.escape(str(m.get('description', '')))}</td>"
            f"<td class='num'>{_money(m.get('current'))}</td>"
            f"<td class='num'>{_money(m.get('prior'))}</td>"
            f"<td class='num'>{_money(m.get('movement'))}</td>"
            f"<td class='num'>{'—' if m.get('pct_change') is None else str(m.get('pct_change')) + '%'}</td></tr>"
            for m in top
        )
    else:
        flux_rows = "<tr><td colspan='6' class='muted'>No movements at or above materiality.</td></tr>"

    # Cash-flow (carried through with its unaudited-draft label)
    cf = st.get("cash_flow")
    cf_block = ""
    if cf:
        cf_block = f"""
      <section>
        <h2>Cash flow <span class="pill warn">{html.escape(str(cf.get('label', 'unaudited_draft')))}</span></h2>
        <p class="caveat">{html.escape(str(cf.get('caveat', '')))}</p>
        <div class="tablewrap card"><table><tbody>
          <tr><td>Cash from operating</td><td class='num'>{_money(cf.get('cash_from_operating'))}</td></tr>
          <tr><td>Cash from investing</td><td class='num'>{_money(cf.get('cash_from_investing'))}</td></tr>
          <tr><td>Cash from financing</td><td class='num'>{_money(cf.get('cash_from_financing'))}</td></tr>
          <tr class='subtotal'><td>Net change in cash</td><td class='num'>{_money(cf.get('net_change_in_cash'))}</td></tr>
        </tbody></table></div>
      </section>"""

    mat = recon.get("materiality_threshold")
    cert_pill_class = "warn" if self_cert is not False else "ok"
    cert_pill_text = "self-certified" if self_cert is not False else "token-locked"

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{ent} — Entity Dashboard {period}</title>
<style>{_STYLE}</style></head>
<body><div class="wrap">
  <header>
    <button class="toggle" id="themeToggle" type="button">◐ theme</button>
    <h1>{ent}</h1>
    <div class="sub">Per-entity close dashboard · period <strong>{period}</strong> · {cur} · state: <strong>{state_name}</strong></div>
    <div class="pills">
      <span class="pill {badge_class}">{badge}</span>
      <span class="pill warn">CF: unaudited draft</span>
      <span class="pill {cert_pill_class}">{cert_pill_text}</span>
    </div>
  </header>
  {cert_banner}
  <div class="note">Single-entity, file-in/file-out tier. The recurring, warehouse-backed,
    multi-tenant version (many entities, row-level isolation, a live embedded dashboard) is NOT
    this file — it reuses <code>data-platform</code>'s row-level security and signed-JWT embed
    (skills <code>rls-policy-authoring</code> / <code>jwt-embed-issuance</code>). Auth and tenant
    isolation are that plugin's owned surface and are not reimplemented here.</div>

  <section>
    <h2>Headline KPIs</h2>
    <div class="kpis">{kpis_html}</div>
    <p class="muted" style="font-size:12.5px">KPIs are derived from the package's own subtotals;
      a KPI that needs data not present (e.g. current-liability detail or an AR line) shows
      <code>n/a</code> rather than a plugged value. Decision-support, not an audit/tax opinion.</p>
  </section>

  <div class="grid2">
    <section>
      <h2>Income statement</h2>
      <div class="tablewrap card"><table><tbody>{is_rows}</tbody></table></div>
    </section>
    <section>
      <h2>Balance sheet</h2>
      <div class="tablewrap card"><table><tbody>{bs_rows}</tbody></table></div>
    </section>
  </div>
  {cf_block}

  <section>
    <h2>Reconciliation exceptions <span class="sub">({len(flagged)} flagged · {n_pass} pass · {n_self} self-supported · materiality {_money(mat)})</span></h2>
    <div class="tablewrap"><table>
      <thead><tr><th>Acct</th><th>Description</th><th class='num'>Book</th><th class='num'>Sub-ledger</th><th class='num'>Diff</th><th>Status</th></tr></thead>
      <tbody>{recon_rows}</tbody>
    </table></div>
  </section>

  <section>
    <h2>Top flux movements <span class="sub">period over period · material only</span></h2>
    <div class="tablewrap"><table>
      <thead><tr><th>Acct</th><th>Description</th><th class='num'>Current</th><th class='num'>Prior</th><th class='num'>Movement</th><th class='num'>%</th></tr></thead>
      <tbody>{flux_rows}</tbody>
    </table></div>
    <p class="muted" style="font-size:13px">The narrative "why" for each movement is authored via the
      <code>variance-commentary</code> skill (reconcile before you narrate).</p>
  </section>
</div>
<script>{_SCRIPT}</script>
</body></html>"""


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description="Render a self-contained per-entity close dashboard from a close-package JSON.")
    p.add_argument("--package", required=True,
                   help="close-package JSON (controller_cycle.py --out-json shape)")
    p.add_argument("--out", help="write dashboard HTML here (else stdout)")
    a = p.parse_args(argv)

    with open(a.package) as fh:
        pkg = json.load(fh)
    doc = render_dashboard(pkg)

    if a.out:
        with open(a.out, "w") as fh:
            fh.write(doc)
        kpi = derive_kpis(pkg)
        print(f"wrote {a.out}  [{pkg.get('statements', {}).get('traceability_badge', '?')}]  "
              f"net income {_money(kpi['net_income'])} {pkg.get('currency', '')}  "
              f"gross margin {_pct(kpi['gross_margin_pct'])}")
    else:
        sys.stdout.write(doc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
