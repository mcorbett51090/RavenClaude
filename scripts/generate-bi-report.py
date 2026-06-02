#!/usr/bin/env python3
"""generate-bi-report.py — build a self-contained, Power-BI/Tableau-style HTML
report for any plugin that ships a `bi-report/data.json`.

Why this exists
---------------
Plugins are agent/skill definitions, not live data sources. This generator gives
a plugin BOTH (1) a ready-to-look-at demo report rendered from SAMPLE data that
ships in the plugin, and (2) the capability to rebuild that same report from a
consumer's REAL data — just replace `bi-report/data.json` (same shape) and re-run.

Design discipline (matches the rest of the marketplace)
-------------------------------------------------------
- **Fully self-contained.** No CDN, no D3/ECharts/Plotly. Charts are hand-rolled
  inline SVG; interactivity (sort / filter / drill-down) is vanilla JS over an
  embedded copy of the data. Works by double-clicking the file.
- **Shared design tokens.** Inlines plugins/ravenclaude-core/dashboard-assets/
  shared-tokens.css at generate-time (teal accent — a consumer-facing surface),
  so the report matches index.html / repo-guide.html.
- **Static-first.** Every chart and the table render server-side (in Python) so
  the report is readable with JS disabled; JS only enhances sort/filter/drill.
- **Plain language (≈5th-grade).** Labels lead with the everyday phrase; the
  jargon (NRR, GRR, IQR…) is the small print. Every metric has a "?" explainer.

Usage
-----
    python3 scripts/generate-bi-report.py            # (re)build every plugin report
    python3 scripts/generate-bi-report.py --check    # fail if any committed report.html is stale
    python3 scripts/generate-bi-report.py --plugin edtech-partner-success
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED_TOKENS = REPO_ROOT / "plugins" / "ravenclaude-core" / "dashboard-assets" / "shared-tokens.css"
PLUGINS_DIR = REPO_ROOT / "plugins"


def _load_shared_tokens() -> str:
    try:
        return SHARED_TOKENS.read_text(encoding="utf-8")
    except OSError:
        return ""


def esc(s) -> str:
    return html.escape(str(s), quote=True)


# ── band helpers ──────────────────────────────────────────────────────────
BAND_VAR = {"green": "var(--rc-ok)", "yellow": "var(--rc-warn)", "red": "var(--rc-danger)"}
BAND_WORD = {"green": "Healthy", "yellow": "Watch", "red": "Act now"}


def band_of(score: int, bands: dict) -> str:
    for name, (lo, hi) in bands.items():
        if lo <= score <= hi:
            return name
    return "red"


# ── tiny inline-SVG chart helpers ───────────────────────────────────────────
def svg_donut(counts: dict, total: int) -> str:
    """Three-segment ring (green/yellow/red) showing the health-band split."""
    if total <= 0:
        total = 1
    r, cx, cy, sw = 52, 70, 70, 22
    circ = 2 * 3.141592653589793 * r
    out = ['<svg viewBox="0 0 140 140" width="140" height="140" role="img" aria-label="Health band split">']
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="var(--rc-border)" stroke-width="{sw}"/>')
    offset = 0.0
    for band in ("green", "yellow", "red"):
        n = counts.get(band, 0)
        if n <= 0:
            continue
        frac = n / total
        seg = circ * frac
        gap = circ - seg
        out.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{BAND_VAR[band]}" '
            f'stroke-width="{sw}" stroke-dasharray="{seg:.2f} {gap:.2f}" '
            f'stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})"/>'
        )
        offset += seg
    out.append(f'<text x="{cx}" y="{cy-2}" text-anchor="middle" font-size="30" font-weight="700" fill="var(--rc-text)">{total}</text>')
    out.append(f'<text x="{cx}" y="{cy+18}" text-anchor="middle" font-size="11" fill="var(--rc-muted)">partners</text>')
    out.append("</svg>")
    return "".join(out)


def svg_line(values, labels, w=620, h=180) -> str:
    """Portfolio trend line with a soft area fill and a band-colored end dot."""
    if not values:
        return ""
    pad_l, pad_r, pad_t, pad_b = 34, 14, 16, 26
    iw, ih = w - pad_l - pad_r, h - pad_t - pad_b
    lo, hi = 0, 100
    n = len(values)
    xs = [pad_l + (iw * i / (n - 1 if n > 1 else 1)) for i in range(n)]
    ys = [pad_t + ih * (1 - (v - lo) / (hi - lo)) for v in values]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    area = f"{pad_l},{pad_t+ih} " + pts + f" {xs[-1]:.1f},{pad_t+ih}"
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" role="img" aria-label="Average health, last 12 weeks">']
    # gridlines + y labels at 0/50/100
    for gv in (0, 50, 100):
        gy = pad_t + ih * (1 - gv / 100)
        out.append(f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{w-pad_r}" y2="{gy:.1f}" stroke="var(--rc-border)" stroke-width="1"/>')
        out.append(f'<text x="{pad_l-6}" y="{gy+4:.1f}" text-anchor="end" font-size="10" fill="var(--rc-faint)">{gv}</text>')
    out.append(f'<polygon points="{area}" fill="var(--rc-teal)" opacity="0.10"/>')
    out.append(f'<polyline points="{pts}" fill="none" stroke="var(--rc-teal)" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>')
    out.append(f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="4.5" fill="var(--rc-teal)"/>')
    # first + last x labels
    out.append(f'<text x="{xs[0]:.1f}" y="{h-8}" text-anchor="start" font-size="10" fill="var(--rc-faint)">{esc(labels[0])}</text>')
    out.append(f'<text x="{xs[-1]:.1f}" y="{h-8}" text-anchor="end" font-size="10" fill="var(--rc-faint)">{esc(labels[-1])}</text>')
    out.append("</svg>")
    return "".join(out)


def svg_spark(values, w=120, h=30) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    rng = (hi - lo) or 1
    n = len(values)
    xs = [w * i / (n - 1 if n > 1 else 1) for i in range(n)]
    ys = [h - 3 - (h - 6) * (v - lo) / rng for v in values]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    up = values[-1] >= values[0]
    color = "var(--rc-ok)" if up else "var(--rc-danger)"
    return (
        f'<svg viewBox="0 0 {w} {h}" width="{w}" height="{h}" class="spark" aria-hidden="true">'
        f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>'
        f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="2.4" fill="{color}"/></svg>'
    )


def svg_components(components, values) -> str:
    """Horizontal bars: one per score component, labeled with its weight."""
    rowh, gap, w = 30, 8, 460
    barx = 150
    barw = w - barx - 44
    out = [f'<svg viewBox="0 0 {w} {len(components)*(rowh+gap)}" width="100%" role="img" aria-label="Score components">']
    y = 4
    for c in components:
        v = int(values.get(c["key"], 0))
        band = "green" if v >= 70 else "yellow" if v >= 50 else "red"
        out.append(f'<text x="0" y="{y+13}" font-size="12" fill="var(--rc-text)">{esc(c["name"])}</text>')
        out.append(f'<text x="0" y="{y+27}" font-size="10" fill="var(--rc-faint)">weight {c["weight"]}% · {c["half_life_days"]}-day memory</text>')
        out.append(f'<rect x="{barx}" y="{y+4}" width="{barw}" height="14" rx="7" fill="var(--rc-border)"/>')
        out.append(f'<rect x="{barx}" y="{y+4}" width="{barw*v/100:.1f}" height="14" rx="7" fill="{BAND_VAR[band]}"/>')
        out.append(f'<text x="{barx+barw+6}" y="{y+15}" font-size="12" font-weight="600" fill="var(--rc-text)">{v}</text>')
        y += rowh + gap
    out.append("</svg>")
    return "".join(out)


def svg_cohort(partners, cohort) -> str:
    """A 0-100 strip with the cohort's middle-half band shaded, the median line,
    and each partner as a dot — 'where does everyone sit vs. their peers'."""
    w, h = 620, 96
    pad_l, pad_r = 14, 14
    iw = w - pad_l - pad_r
    def x(v):
        return pad_l + iw * v / 100
    p25, p75, med = cohort["p25"], cohort["p75"], cohort["median"]
    out = [f'<svg viewBox="0 0 {w} {h}" width="100%" height="{h}" role="img" aria-label="Each partner vs the peer group">']
    track_y = 58
    out.append(f'<rect x="{pad_l}" y="{track_y-4}" width="{iw}" height="8" rx="4" fill="var(--rc-border)"/>')
    out.append(f'<rect x="{x(p25):.1f}" y="{track_y-9}" width="{x(p75)-x(p25):.1f}" height="18" rx="6" fill="var(--rc-teal)" opacity="0.16"/>')
    out.append(f'<line x1="{x(med):.1f}" y1="{track_y-14}" x2="{x(med):.1f}" y2="{track_y+14}" stroke="var(--rc-teal)" stroke-width="2"/>')
    out.append(f'<text x="{x(med):.1f}" y="{track_y-18}" text-anchor="middle" font-size="10" fill="var(--rc-teal)">peer middle ({med})</text>')
    for p in partners:
        out.append(
            f'<circle cx="{x(p["score"]):.1f}" cy="{track_y}" r="5" fill="{BAND_VAR[p["band"]]}" '
            f'stroke="var(--rc-surface)" stroke-width="1.5"><title>{esc(p["name"])}: {p["score"]}</title></circle>'
        )
    for gv in (0, 25, 50, 75, 100):
        out.append(f'<text x="{x(gv):.1f}" y="{h-6}" text-anchor="middle" font-size="10" fill="var(--rc-faint)">{gv}</text>')
    out.append("</svg>")
    return "".join(out)


# ── CSS (kept brace-free of f-strings) ──────────────────────────────────────
REPORT_CSS = """
:root {
  --bg: var(--rc-bg); --surface: var(--rc-surface); --surface-2: var(--rc-surface-2);
  --border: var(--rc-border); --border-strong: var(--rc-border-strong);
  --text: var(--rc-text); --muted: var(--rc-muted); --faint: var(--rc-faint);
  --accent: var(--rc-teal); --font-sans: var(--rc-font-sans); --font-mono: var(--rc-font-mono);
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text); font-family: var(--font-sans);
  font-size: 15px; line-height: 1.5; -webkit-font-smoothing: antialiased; }
a { color: var(--accent); }
.wrap { max-width: 1180px; margin: 0 auto; padding: 28px clamp(16px, 4vw, 36px) 80px; }
.rhead { display: flex; align-items: flex-start; gap: 16px; flex-wrap: wrap; margin-bottom: 6px; }
.rhead h1 { font-size: clamp(1.5rem, 3vw, 2rem); margin: 0; letter-spacing: -0.02em; }
.rhead .stamp { margin-left: auto; font-size: 0.78rem; color: var(--faint); text-align: right; }
.synthetic { display: inline-block; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.04em;
  text-transform: uppercase; color: var(--rc-warn-fg); background: var(--rc-warn-bg);
  border-radius: var(--rc-radius-pill); padding: 2px 10px; margin-top: 6px; }
.lede { color: var(--muted); max-width: 70ch; margin: 4px 0 18px; }
.rule { height: 1px; border: 0; background: linear-gradient(90deg, transparent, var(--accent) 50%, transparent); opacity: 0.5; margin: 22px 0; }
.dq { display: flex; gap: 10px; align-items: flex-start; background: var(--rc-warn-bg); color: var(--rc-warn-fg);
  border: 1px solid var(--rc-border); border-radius: var(--rc-radius); padding: 12px 14px; margin-bottom: 20px; font-size: 0.86rem; }
.dq b { font-weight: 700; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin-bottom: 8px; }
.kpi { background: var(--surface); border: 1px solid var(--border); border-radius: var(--rc-radius-lg);
  box-shadow: var(--rc-shadow-sm); padding: 16px 18px; transition: box-shadow .18s ease, transform .18s ease; }
.kpi:hover { box-shadow: var(--rc-shadow-md); transform: translateY(-2px); }
.kpi .k { display: flex; align-items: center; gap: 6px; color: var(--muted); font-size: 0.8rem; }
.kpi .v { font-size: 1.9rem; font-weight: 700; line-height: 1.1; margin-top: 4px; }
.kpi .d { font-size: 0.78rem; margin-top: 2px; }
.kpi .d.up { color: var(--rc-ok); } .kpi .d.down { color: var(--rc-danger); } .kpi .d.flat { color: var(--faint); }
.kpi .full { font-size: 0.72rem; color: var(--faint); font-family: var(--font-mono); }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 820px) { .grid2 { grid-template-columns: 1fr; } }
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--rc-radius-lg);
  box-shadow: var(--rc-shadow-sm); padding: 18px 20px; }
.panel h2 { font-size: 1.05rem; margin: 0 0 2px; letter-spacing: -0.01em; }
.panel .sub { color: var(--faint); font-size: 0.8rem; margin: 0 0 12px; }
.donut-row { display: flex; align-items: center; gap: 18px; }
.legend { display: flex; flex-direction: column; gap: 6px; font-size: 0.86rem; }
.legend .li { display: flex; align-items: center; gap: 8px; }
.legend .sw { width: 12px; height: 12px; border-radius: 3px; flex: 0 0 auto; }
.info { display: inline-flex; align-items: center; justify-content: center; width: 16px; height: 16px;
  border-radius: 50%; border: 1px solid var(--border-strong); background: var(--surface); color: var(--muted);
  font-size: 10px; font-weight: 700; cursor: help; flex: 0 0 auto; }
.toolbar { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin: 22px 0 12px; }
.toolbar input, .toolbar select { height: 38px; padding: 0 12px; border-radius: var(--rc-radius-sm);
  background: var(--surface); border: 1px solid var(--border-strong); color: var(--text); font: inherit; font-size: 0.88rem; }
.toolbar input { flex: 1; min-width: 200px; }
.toolbar .seg { display: inline-flex; border: 1px solid var(--border-strong); border-radius: var(--rc-radius-sm); overflow: hidden; }
.toolbar .seg button { background: var(--surface); border: 0; padding: 8px 12px; font: inherit; font-size: 0.82rem; cursor: pointer; color: var(--muted); }
.toolbar .seg button[aria-pressed="true"] { background: var(--accent); color: #fff; }
table.partners { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
table.partners th { text-align: left; padding: 10px 10px; border-bottom: 1px solid var(--border-strong);
  color: var(--muted); font-weight: 600; cursor: pointer; white-space: nowrap; user-select: none; }
table.partners th .arr { color: var(--faint); font-size: 0.7rem; }
table.partners td { padding: 10px 10px; border-bottom: 1px solid var(--border); vertical-align: middle; }
table.partners tr.prow { cursor: pointer; }
table.partners tr.prow:hover { background: var(--surface-2); }
.scorebadge { display: inline-flex; align-items: center; justify-content: center; min-width: 34px; padding: 2px 8px;
  border-radius: var(--rc-radius-pill); font-weight: 700; font-size: 0.82rem; color: #fff; }
.bandtag { display: inline-flex; align-items: center; gap: 6px; font-size: 0.8rem; }
.bandtag .dot { width: 9px; height: 9px; border-radius: 50%; }
.dchip { display: inline-block; font-size: 0.78rem; }
.dchip.up { color: var(--rc-ok); } .dchip.down { color: var(--rc-danger); } .dchip.flat { color: var(--faint); }
.flagcell { font-size: 1.1rem; }
.drow td { background: var(--surface-2); padding: 0; }
.drawer { padding: 18px 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
@media (max-width: 820px) { .drawer { grid-template-columns: 1fr; } }
.drawer h3 { margin: 0 0 8px; font-size: 0.95rem; }
.flaglist { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.flaglist li { background: var(--rc-danger-bg); color: var(--rc-danger-fg); border-radius: var(--rc-radius-sm);
  padding: 7px 10px; font-size: 0.82rem; }
.flaglist li.none { background: var(--rc-ok-bg); color: var(--rc-ok-fg); }
.kv { display: grid; grid-template-columns: auto 1fr; gap: 4px 14px; font-size: 0.84rem; }
.kv dt { color: var(--muted); } .kv dd { margin: 0; font-weight: 600; }
.hidden { display: none !important; }
.foot { margin-top: 30px; color: var(--faint); font-size: 0.78rem; }
[data-theme="dark"] .toolbar .seg button[aria-pressed="true"], [data-theme="dark"] .scorebadge { color: #14110d; }
"""

REPORT_JS = """
(function(){
  var DATA = window.__BI_DATA__ || {partners:[]};
  var bandVar = {green:'var(--rc-ok)', yellow:'var(--rc-warn)', red:'var(--rc-danger)'};
  var tbody = document.getElementById('pbody');
  if(!tbody) return;
  var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr.prow'));
  var search = document.getElementById('psearch');
  var sortState = {key:'score', dir:'desc'};

  function applyFilter(){
    var q = (search && search.value || '').toLowerCase();
    var band = document.querySelector('.seg button[aria-pressed="true"]');
    band = band ? band.getAttribute('data-band') : 'all';
    rows.forEach(function(r){
      var name = r.getAttribute('data-name').toLowerCase();
      var psm = r.getAttribute('data-psm').toLowerCase();
      var rb = r.getAttribute('data-band');
      var show = (q==='' || name.indexOf(q)>=0 || psm.indexOf(q)>=0) && (band==='all' || rb===band);
      r.classList.toggle('hidden', !show);
      var d = r.nextElementSibling;
      if(d && d.classList.contains('drow')){ d.classList.add('hidden'); }
    });
  }
  function sortBy(key){
    if(sortState.key===key){ sortState.dir = sortState.dir==='asc'?'desc':'asc'; }
    else { sortState.key=key; sortState.dir = (key==='name'||key==='psm')?'asc':'desc'; }
    var dir = sortState.dir==='asc'?1:-1;
    rows.sort(function(a,b){
      var av=a.getAttribute('data-'+key), bv=b.getAttribute('data-'+key);
      var an=parseFloat(av), bn=parseFloat(bv);
      if(!isNaN(an)&&!isNaN(bn)){ return (an-bn)*dir; }
      return av.localeCompare(bv)*dir;
    });
    rows.forEach(function(r){ var d=r.nextElementSibling; tbody.appendChild(r); if(d&&d.classList.contains('drow')) tbody.appendChild(d); });
    document.querySelectorAll('th[data-key] .arr').forEach(function(el){ el.textContent=''; });
    var th = document.querySelector('th[data-key="'+key+'"] .arr'); if(th) th.textContent = sortState.dir==='asc'?'▲':'▼';
  }
  if(search) search.addEventListener('input', applyFilter);
  document.querySelectorAll('.seg button').forEach(function(b){
    b.addEventListener('click', function(){
      document.querySelectorAll('.seg button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
      b.setAttribute('aria-pressed','true'); applyFilter();
    });
  });
  document.querySelectorAll('th[data-key]').forEach(function(th){
    th.addEventListener('click', function(){ sortBy(th.getAttribute('data-key')); });
  });
  rows.forEach(function(r){
    r.addEventListener('click', function(){
      var d = r.nextElementSibling;
      if(d && d.classList.contains('drow')) d.classList.toggle('hidden');
    });
  });
})();
"""


def render_report(data: dict, plugin: str, tokens: str) -> str:
    rep = data.get("report", {})
    bands = data.get("bands", {"green": [70, 100], "yellow": [50, 69], "red": [0, 49]})
    components = data.get("components", [])
    partners = data.get("partners", [])
    for p in partners:
        p.setdefault("band", band_of(int(p.get("score", 0)), bands))
    counts = {"green": 0, "yellow": 0, "red": 0}
    for p in partners:
        counts[p["band"]] = counts.get(p["band"], 0) + 1
    total = len(partners)

    # KPI cards
    kpi_html = []
    for k in data.get("kpis", []):
        d = k.get("delta", 0)
        good = k.get("good", "up")
        if d == 0:
            cls, arrow = "flat", "→"
        else:
            rising = d > 0
            is_good = (rising and good == "up") or (not rising and good == "down")
            cls = "up" if is_good else "down"
            arrow = "▲" if rising else "▼"
        unit = k.get("unit", "")
        kpi_html.append(
            f'<div class="kpi"><div class="k">{esc(k["label"])}'
            f'<span class="info" tabindex="0" title="{esc(k.get("plain",""))}">?</span></div>'
            f'<div class="v">{esc(k["value"])}{esc(unit)}</div>'
            f'<div class="d {cls}">{arrow} {abs(d)}{esc(unit) if unit=="%" else ""} vs last period</div>'
            f'<div class="full">{esc(k.get("short",""))}</div></div>'
        )

    # legend
    legend = []
    for band in ("green", "yellow", "red"):
        lo, hi = bands.get(band, [0, 0])
        legend.append(
            f'<div class="li"><span class="sw" style="background:{BAND_VAR[band]}"></span>'
            f'<b style="font-weight:700">{counts.get(band,0)}</b>&nbsp;{BAND_WORD[band]} '
            f'<span style="color:var(--faint)">({lo}–{hi})</span></div>'
        )

    cohort = data.get("cohort", {})

    # partner rows + drill-down drawers
    prows = []
    for p in partners:
        b = p["band"]
        d = p.get("delta", 0)
        dcls = "flat" if d == 0 else ("up" if d > 0 else "down")
        darr = "→" if d == 0 else ("▲" if d > 0 else "▼")
        flag_n = len(p.get("flags", []))
        flagcell = f'<span class="flagcell" title="{flag_n} red flag(s)">{"⚠️"*min(flag_n,3)}</span>' if flag_n else '<span style="color:var(--faint)">—</span>'
        seg_word = {"k12": "K-12", "higher-ed": "Higher ed", "corp-ld": "Corporate L&D", "mixed": "Mixed"}.get(p.get("segment", ""), p.get("segment", ""))
        prows.append(
            f'<tr class="prow" data-name="{esc(p["name"])}" data-psm="{esc(p.get("psm",""))}" '
            f'data-band="{b}" data-score="{p["score"]}" data-delta="{d}" data-renewal="{esc(p.get("renewal",""))}">'
            f'<td><b>{esc(p["name"])}</b><div style="color:var(--faint);font-size:0.78rem">{esc(seg_word)}</div></td>'
            f'<td><span class="scorebadge" style="background:{BAND_VAR[b]}">{p["score"]}</span></td>'
            f'<td><span class="dchip {dcls}">{darr} {abs(d)}</span></td>'
            f'<td><span class="bandtag"><span class="dot" style="background:{BAND_VAR[b]}"></span>{BAND_WORD[b]}</span></td>'
            f'<td>{flagcell}</td>'
            f'<td>{esc(p.get("play",""))}</td>'
            f'<td>{svg_spark(p.get("spark",[]))}</td>'
            f'<td>{esc(p.get("psm",""))}</td>'
            f'<td style="white-space:nowrap">{esc(p.get("renewal",""))}</td>'
            f'</tr>'
        )
        # drawer
        if p.get("flags"):
            flags = "".join(f"<li>{esc(f)}</li>" for f in p["flags"])
        else:
            flags = '<li class="none">No red flags. Steady as she goes.</li>'
        drawer = (
            f'<tr class="drow hidden"><td colspan="9"><div class="drawer">'
            f'<div><h3>What’s moving the score</h3>{svg_components(components, p.get("components",{}))}</div>'
            f'<div><h3>Red flags &amp; the basics</h3><ul class="flaglist">{flags}</ul>'
            f'<dl class="kv" style="margin-top:12px">'
            f'<dt>Recommended play</dt><dd>{esc(p.get("play",""))}</dd>'
            f'<dt>Last time we talked</dt><dd>{esc(p.get("last_touch","—"))}</dd>'
            f'<dt>Next check-in (QBR)</dt><dd>{esc(p.get("next_qbr","—"))}</dd>'
            f'<dt>Contract renews</dt><dd>{esc(p.get("renewal","—"))}</dd>'
            f'<dt>Owner (PSM)</dt><dd>{esc(p.get("psm","—"))}</dd>'
            f'</dl></div></div></td></tr>'
        )
        prows.append(drawer)

    # data-quality banner
    dq = data.get("data_quality_flags", [])
    # also lift any partner rostering-stale flags into the banner
    for p in partners:
        for f in p.get("flags", []):
            if "stale" in f.lower() or "sync" in f.lower():
                dq.append({"partner": p["name"], "issue": f})
    dq_html = ""
    if dq:
        items = "".join(f"<div><b>{esc(x.get('partner',''))}:</b> {esc(x.get('issue',''))}</div>" for x in dq)
        dq_html = (
            f'<div class="dq" role="status"><span aria-hidden="true">⚠️</span>'
            f'<div><b>Data-quality check.</b> A partner can look red just because their data is stale — '
            f'check these before you act:<div style="margin-top:6px;display:flex;flex-direction:column;gap:4px">{items}</div></div></div>'
        )

    title = esc(rep.get("title", "Portfolio Report"))
    subtitle = esc(rep.get("subtitle", ""))
    refreshed = esc(rep.get("refreshed", ""))
    synthetic = '<div class="synthetic">Sample data · not real partners</div>' if rep.get("synthetic") else ""

    data_json = json.dumps({"partners": [{"name": p["name"], "band": p["band"], "score": p["score"]} for p in partners]})

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title} — {esc(plugin)}</title>
<style>
/*__SHARED_TOKENS__*/
{REPORT_CSS}
</style>
</head>
<body>
<div class="wrap">
  <div class="rhead">
    <div>
      <h1>{title}</h1>
      {synthetic}
    </div>
    <div class="stamp">Updated {refreshed}<br/>Owner: {esc(rep.get("owner",""))}</div>
  </div>
  <p class="lede">{subtitle}</p>
  {dq_html}

  <div class="kpis">
    {''.join(kpi_html)}
  </div>

  <hr class="rule"/>

  <div class="grid2">
    <div class="panel">
      <h2>How the whole book looks</h2>
      <p class="sub">Every partner sorted into three buckets by health score.</p>
      <div class="donut-row">{svg_donut(counts, total)}<div class="legend">{''.join(legend)}</div></div>
    </div>
    <div class="panel">
      <h2>Average health, last 12 weeks</h2>
      <p class="sub">The average score across all partners, week by week. Up is good.</p>
      {svg_line(data.get("portfolio_trend", []), data.get("trend_weeks", []))}
    </div>
  </div>

  <div class="panel" style="margin-top:16px">
    <h2>Where each partner sits vs. its peers
      <span class="info" tabindex="0" title="The shaded band is the middle half of the peer group (25th to 75th score). The line is the peer middle (median). Each dot is one partner.">?</span>
    </h2>
    <p class="sub">Peer group: {esc(cohort.get("label","—"))} · {cohort.get("size","?")} partners. A dot to the right of the band is doing better than most peers.</p>
    {svg_cohort(partners, cohort) if cohort else ''}
  </div>

  <div class="toolbar">
    <input id="psearch" type="search" placeholder="Search a partner or owner…" aria-label="Search partners"/>
    <div class="seg" role="group" aria-label="Filter by health band">
      <button data-band="all" aria-pressed="true">All</button>
      <button data-band="green" aria-pressed="false">Healthy</button>
      <button data-band="yellow" aria-pressed="false">Watch</button>
      <button data-band="red" aria-pressed="false">Act now</button>
    </div>
  </div>

  <div class="panel" style="padding:6px 8px">
    <table class="partners">
      <thead><tr>
        <th data-key="name">Partner <span class="arr"></span></th>
        <th data-key="score">Score <span class="arr">▼</span></th>
        <th data-key="delta">Change <span class="arr"></span></th>
        <th>Health</th>
        <th>Flags</th>
        <th>Next play</th>
        <th>12-week trend</th>
        <th data-key="psm">Owner <span class="arr"></span></th>
        <th data-key="renewal">Renews <span class="arr"></span></th>
      </tr></thead>
      <tbody id="pbody">
        {''.join(prows)}
      </tbody>
    </table>
  </div>
  <p class="sub" style="margin-top:8px">Tip: click any row to open the drill-down (what’s moving the score + red flags). Click a column header to sort.</p>

  <p class="foot">
    Self-contained report — no internet needed. Built by <code>scripts/generate-bi-report.py</code> from
    <code>plugins/{esc(plugin)}/bi-report/data.json</code>. Replace that file with a real export (same shape) and re-run to rebuild.
    Scores are 0–100; bands: Healthy 70+, Watch 50–69, Act now under 50.
  </p>
</div>
<script>window.__BI_DATA__ = {data_json};</script>
<script>
{REPORT_JS}
</script>
</body>
</html>
"""
    return page.replace("/*__SHARED_TOKENS__*/", tokens)


def discover_plugins(only: str | None):
    found = []
    for d in sorted(PLUGINS_DIR.iterdir()):
        if not d.is_dir():
            continue
        if only and d.name != only:
            continue
        data_file = d / "bi-report" / "data.json"
        if data_file.exists():
            found.append((d.name, data_file, d / "report.html"))
    return found


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build self-contained BI reports for plugins that ship bi-report/data.json")
    ap.add_argument("--check", action="store_true", help="fail (exit 1) if any committed report.html is stale")
    ap.add_argument("--plugin", help="only build this plugin")
    args = ap.parse_args(argv)

    tokens = _load_shared_tokens()
    targets = discover_plugins(args.plugin)
    if not targets:
        print("no plugins with bi-report/data.json found", file=sys.stderr)
        return 0

    stale = []
    for name, data_file, out in targets:
        try:
            data = json.loads(data_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            print(f"[error] {name}: cannot read {data_file}: {e}", file=sys.stderr)
            return 2
        page = render_report(data, name, tokens)
        if args.check:
            current = out.read_text(encoding="utf-8") if out.exists() else ""
            if current != page:
                stale.append(name)
        else:
            out.write_text(page, encoding="utf-8")
            print(f"[ok] wrote {out.relative_to(REPO_ROOT)} ({len(page)//1024} KB, {len(data.get('partners',[]))} partners)")

    if args.check:
        if stale:
            print(f"STALE report.html for: {', '.join(stale)} — run scripts/generate-bi-report.py", file=sys.stderr)
            return 1
        print("all BI reports fresh")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
