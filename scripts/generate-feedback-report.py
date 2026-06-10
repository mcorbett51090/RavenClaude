#!/usr/bin/env python3
"""generate-feedback-report.py — build the "Problems & Resolutions" view.

Why this exists
---------------
Matt's ask, verbatim: "I want to see all the problems users are facing and how
they're resolving it." The scenario corpus already holds exactly that — each
`plugins/<plugin>/scenarios/*.md` file is a problem → context → tried →
resolution field-note with a 9-field YAML frontmatter. This generator READS that
corpus (it writes nothing back) and emits ONE self-contained, offline HTML view:
a filterable table of every problem and its resolution, plus a top summary.

The seed-vs-organic distinction (the load-bearing feature)
----------------------------------------------------------
The corpus is ~361 files but ~357 are a 2-day bulk *seed* drop (synthetic
authoring), and only ~4 are *organic* contributions from real engagements (the
power-platform 2026-05-21/26 set). FORGE's feedback-mechanism-eval found that the
seed inflates the count and hides the handful of real user problems. So the view
MUST let Matt distinguish the two. We classify a scenario as **seed** when its
`contributed_at` date is a *bulk-drop* date — a date on which an unusually large
number of scenarios were contributed at once (detected dynamically from the data,
see `SEED_DROP_MIN`). Everything else is **organic**. This is deterministic and
self-adjusting: when real organic contributions accumulate on ordinary days they
are never mis-tagged as seed.

Design discipline (matches scripts/generate-bi-report.py)
---------------------------------------------------------
- **Fully self-contained.** No CDN. Inline CSS/JS, vanilla JS over embedded data.
  Works by double-clicking the file.
- **Shared design tokens.** Inlines the marketplace shared-tokens.css at
  generate-time so the report matches index.html / the BI reports.
- **Static-first.** The whole table renders server-side (in Python); JS only adds
  client-side filter/search/sort.
- **Deterministic output.** NO wall-clock timestamp — the "as of" date is derived
  from the newest scenario's `contributed_at`, so `--check` is stable run-to-run.
- **Privacy (FORGE R-PRIV).** Renders ONLY fields that already ship in the
  committed scenario files. Adds no env / tenant / auth / role data. The scenarios
  are already consumer-shipped, so this is "render what's there," nothing new.
- **stdlib-only, fail-safe.** A malformed scenario degrades to placeholders; the
  generator never crashes on one bad file.

Usage
-----
    python3 scripts/generate-feedback-report.py            # (re)build feedback-report.html
    python3 scripts/generate-feedback-report.py --check    # fail (exit 1) if the committed file is stale
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED_TOKENS = REPO_ROOT / "plugins" / "ravenclaude-core" / "dashboard-assets" / "shared-tokens.css"
PLUGINS_DIR = REPO_ROOT / "plugins"
OUT_FILE = REPO_ROOT / "feedback-report.html"

# A `contributed_at` date carrying at least this many scenarios is treated as a
# bulk *seed* drop (synthetic authoring), not organic contribution. The two real
# seed dates (2026-06-05 = 262, 2026-06-08 = 95) sit far above this; the organic
# power-platform days (1-3 files each) sit far below. Picked to be robust to a
# realistic future organic burst (a consultant logging a handful in one day) while
# still catching the bulk authoring drops.
SEED_DROP_MIN = 20

# Sections, in the body, whose text we treat as the "resolution / what worked".
RESOLUTION_HEADINGS = ("Resolution",)
PROBLEM_HEADINGS = ("Problem",)


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def _load_shared_tokens() -> str:
    try:
        return SHARED_TOKENS.read_text(encoding="utf-8")
    except OSError:
        return ""


# ── frontmatter + body parsing (no PyYAML; stdlib-only, fail-safe) ───────────
_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _parse_scalar(raw: str):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        return [p.strip().strip("\"'") for p in inner.split(",") if p.strip()]
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    return raw


def parse_frontmatter(text: str):
    """Return (frontmatter_dict, body_str). Fail-safe: returns ({}, text) on any
    shape we don't recognize."""
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    fm_block, body = m.group(1), m.group(2)
    fm = {}
    for line in fm_block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        if not key or line[0] in (" ", "\t"):
            # nested / list-continuation lines — the flat 9-field schema has none,
            # so skip defensively rather than mis-parse.
            continue
        fm[key] = _parse_scalar(val)
    return fm, body


def extract_section(body: str, headings) -> str:
    """Pull the prose under the first matching '## <heading>' up to the next '## '.
    Returns a single collapsed-whitespace string (markdown stripped lightly)."""
    for h in headings:
        pat = re.compile(r"^##\s+" + re.escape(h) + r"\s*\n(.*?)(?=^##\s|\Z)", re.DOTALL | re.MULTILINE)
        m = pat.search(body)
        if m:
            return _clean_prose(m.group(1))
    return ""


def _clean_prose(s: str) -> str:
    # drop fenced code blocks (keep the view readable), strip md emphasis/links,
    # collapse whitespace. Best-effort — this is display text, not data.
    s = re.sub(r"```.*?```", " ", s, flags=re.DOTALL)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)  # [text](url) -> text
    s = re.sub(r"[*_`#>]+", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def shorten(s: str, limit: int = 240) -> str:
    s = s.strip()
    if len(s) <= limit:
        return s
    cut = s[: limit - 1]
    sp = cut.rfind(" ")
    if sp > limit * 0.6:
        cut = cut[:sp]
    return cut.rstrip(" .,;:") + "…"


# ── corpus load ──────────────────────────────────────────────────────────────
def load_scenarios():
    records = []
    for path in sorted(PLUGINS_DIR.glob("*/scenarios/*.md")):
        if path.name == "README.md":
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        fm, body = parse_frontmatter(text)
        problem = extract_section(body, PROBLEM_HEADINGS)
        resolution = extract_section(body, RESOLUTION_HEADINGS)
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]
        records.append(
            {
                "scenario_id": str(fm.get("scenario_id", path.stem) or path.stem),
                "contributed_at": str(fm.get("contributed_at", "") or ""),
                "plugin": str(fm.get("plugin", path.parts[-3]) or path.parts[-3]),
                "product": str(fm.get("product", "") or ""),
                "product_version": str(fm.get("product_version", "") or ""),
                "scope": str(fm.get("scope", "") or "unknown"),
                "tags": [str(t) for t in tags],
                "confidence": str(fm.get("confidence", "") or ""),
                "reviewed": str(fm.get("reviewed", "")),
                "problem": problem or "(no Problem section found)",
                "resolution": resolution or "(no Resolution section found)",
                "path": rel,
            }
        )
    return records


def classify_origin(records):
    """Tag each record 'seed' or 'organic'. Seed = contributed on a bulk-drop date
    (>= SEED_DROP_MIN scenarios share that date). Deterministic from the data."""
    by_date = Counter(r["contributed_at"] for r in records if r["contributed_at"])
    seed_dates = {d for d, n in by_date.items() if n >= SEED_DROP_MIN}
    for r in records:
        r["origin"] = "seed" if r["contributed_at"] in seed_dates else "organic"
    return seed_dates


# ── HTML render ──────────────────────────────────────────────────────────────
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
.wrap { max-width: 1240px; margin: 0 auto; padding: 28px clamp(16px, 4vw, 36px) 80px; }
.rhead { display: flex; align-items: flex-start; gap: 16px; flex-wrap: wrap; margin-bottom: 6px; }
.rhead h1 { font-size: clamp(1.5rem, 3vw, 2rem); margin: 0; letter-spacing: -0.02em; }
.rhead .stamp { margin-left: auto; font-size: 0.78rem; color: var(--faint); text-align: right; }
.lede { color: var(--muted); max-width: 78ch; margin: 4px 0 18px; }
.rule { height: 1px; border: 0; background: linear-gradient(90deg, transparent, var(--accent) 50%, transparent); opacity: 0.5; margin: 22px 0; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin-bottom: 8px; }
.kpi { background: var(--surface); border: 1px solid var(--border); border-radius: var(--rc-radius-lg);
  box-shadow: var(--rc-shadow-sm); padding: 16px 18px; }
.kpi .k { display: flex; align-items: center; gap: 6px; color: var(--muted); font-size: 0.8rem; }
.kpi .v { font-size: 1.9rem; font-weight: 700; line-height: 1.1; margin-top: 4px; }
.kpi .d { font-size: 0.78rem; margin-top: 2px; color: var(--faint); }
.dq { display: flex; gap: 10px; align-items: flex-start; background: var(--rc-warn-bg); color: var(--rc-warn-fg);
  border: 1px solid var(--rc-border); border-radius: var(--rc-radius); padding: 12px 14px; margin: 18px 0; font-size: 0.86rem; }
.dq b { font-weight: 700; }
.panel { background: var(--surface); border: 1px solid var(--border); border-radius: var(--rc-radius-lg);
  box-shadow: var(--rc-shadow-sm); padding: 18px 20px; }
.panel h2 { font-size: 1.05rem; margin: 0 0 2px; letter-spacing: -0.01em; }
.panel .sub { color: var(--faint); font-size: 0.8rem; margin: 0 0 12px; }
.splitbar { display: flex; height: 26px; border-radius: var(--rc-radius-pill); overflow: hidden; border: 1px solid var(--border); }
.splitbar .seg { display: flex; align-items: center; justify-content: center; font-size: 0.74rem; font-weight: 700; color: #fff; white-space: nowrap; }
.splitbar .organic { background: var(--rc-teal); }
.splitbar .seed { background: var(--rc-faint); }
.minilegend { display: flex; gap: 16px; margin-top: 8px; font-size: 0.8rem; color: var(--muted); }
.minilegend .li { display: flex; align-items: center; gap: 6px; }
.minilegend .sw { width: 11px; height: 11px; border-radius: 3px; }
.barlist { display: grid; gap: 6px; }
.barlist .row { display: grid; grid-template-columns: 160px 1fr 40px; align-items: center; gap: 8px; font-size: 0.84rem; }
.barlist .row .bar { background: var(--border); border-radius: var(--rc-radius-pill); height: 12px; overflow: hidden; }
.barlist .row .bar > span { display: block; height: 100%; background: var(--rc-teal); }
.barlist .row .n { text-align: right; font-variant-numeric: tabular-nums; color: var(--muted); }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 880px) { .grid2 { grid-template-columns: 1fr; } }
.toolbar { display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin: 22px 0 12px; }
.toolbar input, .toolbar select { height: 38px; padding: 0 12px; border-radius: var(--rc-radius-sm);
  background: var(--surface); border: 1px solid var(--border-strong); color: var(--text); font: inherit; font-size: 0.88rem; }
.toolbar input { flex: 1; min-width: 220px; }
.toolbar .seg { display: inline-flex; border: 1px solid var(--border-strong); border-radius: var(--rc-radius-sm); overflow: hidden; }
.toolbar .seg button { background: var(--surface); border: 0; padding: 8px 12px; font: inherit; font-size: 0.82rem; cursor: pointer; color: var(--muted); }
.toolbar .seg button[aria-pressed="true"] { background: var(--accent); color: #fff; }
.count { color: var(--faint); font-size: 0.82rem; margin-left: auto; }
table.t { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
table.t th { text-align: left; padding: 10px 10px; border-bottom: 1px solid var(--border-strong);
  color: var(--muted); font-weight: 600; cursor: pointer; white-space: nowrap; user-select: none; vertical-align: bottom; }
table.t th .arr { color: var(--faint); font-size: 0.7rem; }
table.t td { padding: 11px 10px; border-bottom: 1px solid var(--border); vertical-align: top; }
table.t tr.r:hover { background: var(--surface-2); }
.prob { font-weight: 600; }
.reso { color: var(--muted); }
.tagrow { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 5px; }
.tag { font-size: 0.7rem; background: var(--surface-2); border: 1px solid var(--border); color: var(--muted);
  border-radius: var(--rc-radius-pill); padding: 1px 8px; }
.pill { display: inline-block; font-size: 0.72rem; font-weight: 700; border-radius: var(--rc-radius-pill); padding: 2px 9px; white-space: nowrap; }
.pill.organic { background: var(--rc-teal); color: #fff; }
.pill.seed { background: var(--surface-2); color: var(--muted); border: 1px solid var(--border); }
.scope { font-size: 0.78rem; color: var(--muted); }
.meta { font-size: 0.76rem; color: var(--faint); font-family: var(--font-mono); white-space: nowrap; }
.hidden { display: none !important; }
.empty { padding: 24px; text-align: center; color: var(--faint); }
.foot { margin-top: 30px; color: var(--faint); font-size: 0.78rem; }
[data-theme="dark"] .splitbar .organic, [data-theme="dark"] .pill.organic,
[data-theme="dark"] .toolbar .seg button[aria-pressed="true"] { color: #14110d; }
"""

REPORT_JS = """
(function(){
  var tbody = document.getElementById('tbody');
  if(!tbody) return;
  var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr.r'));
  var search = document.getElementById('q');
  var pluginSel = document.getElementById('fplugin');
  var scopeSel = document.getElementById('fscope');
  var count = document.getElementById('count');
  var empty = document.getElementById('empty');
  var sortDir = {};

  function originBtn(){
    var b = document.querySelector('.seg button[aria-pressed="true"]');
    return b ? b.getAttribute('data-origin') : 'all';
  }
  function applyFilter(){
    var q = (search && search.value || '').toLowerCase();
    var pl = pluginSel ? pluginSel.value : 'all';
    var sc = scopeSel ? scopeSel.value : 'all';
    var origin = originBtn();
    var shown = 0;
    rows.forEach(function(r){
      var hay = r.getAttribute('data-search') || '';
      var ok = (q==='' || hay.indexOf(q)>=0)
        && (pl==='all' || r.getAttribute('data-plugin')===pl)
        && (sc==='all' || r.getAttribute('data-scope')===sc)
        && (origin==='all' || r.getAttribute('data-origin')===origin);
      r.classList.toggle('hidden', !ok);
      if(ok) shown++;
    });
    if(count) count.textContent = shown + ' of ' + rows.length + ' shown';
    if(empty) empty.classList.toggle('hidden', shown!==0);
  }
  function sortBy(key, th){
    var dir = sortDir[key]==='asc' ? 'desc' : 'asc'; sortDir = {}; sortDir[key]=dir;
    var m = dir==='asc'?1:-1;
    rows.sort(function(a,b){
      var av=(a.getAttribute('data-'+key)||'').toLowerCase(), bv=(b.getAttribute('data-'+key)||'').toLowerCase();
      if(av<bv) return -1*m; if(av>bv) return 1*m; return 0;
    });
    rows.forEach(function(r){ tbody.appendChild(r); });
    document.querySelectorAll('th[data-key] .arr').forEach(function(el){ el.textContent=''; });
    var a=th.querySelector('.arr'); if(a) a.textContent = dir==='asc'?'▲':'▼';
  }
  if(search) search.addEventListener('input', applyFilter);
  if(pluginSel) pluginSel.addEventListener('change', applyFilter);
  if(scopeSel) scopeSel.addEventListener('change', applyFilter);
  document.querySelectorAll('.seg button').forEach(function(b){
    b.addEventListener('click', function(){
      document.querySelectorAll('.seg button').forEach(function(x){ x.setAttribute('aria-pressed','false'); });
      b.setAttribute('aria-pressed','true'); applyFilter();
    });
  });
  document.querySelectorAll('th[data-key]').forEach(function(th){
    th.addEventListener('click', function(){ sortBy(th.getAttribute('data-key'), th); });
  });
  applyFilter();
})();
"""


def _bar_rows(counter, total, limit=None):
    items = counter.most_common(limit)
    mx = max([n for _, n in items], default=1)
    out = []
    for label, n in items:
        pct = (n / mx * 100) if mx else 0
        out.append(
            f'<div class="row"><span title="{esc(label)}">{esc(label)}</span>'
            f'<span class="bar"><span style="width:{pct:.1f}%"></span></span>'
            f'<span class="n">{n}</span></div>'
        )
    return "".join(out)


def render(records, seed_dates, tokens: str) -> str:
    total = len(records)
    organic = [r for r in records if r["origin"] == "organic"]
    seed = [r for r in records if r["origin"] == "seed"]
    n_org, n_seed = len(organic), len(seed)

    # "as of" date — derived (deterministic), NOT wall-clock.
    dates = sorted([r["contributed_at"] for r in records if r["contributed_at"]])
    as_of = dates[-1] if dates else "—"

    by_plugin = Counter(r["plugin"] for r in records)
    by_scope = Counter(r["scope"] for r in records)

    # KPI cards
    kpis = [
        ("Problems logged", str(total), "every scenario in the corpus"),
        ("Real user problems", str(n_org), "organic — from actual engagements"),
        ("Seed examples", str(n_seed), "synthetic bulk-authored starter set"),
        ("Plugins covered", str(len(by_plugin)), "plugins with at least one scenario"),
    ]
    kpi_html = "".join(
        f'<div class="kpi"><div class="k">{esc(k)}</div><div class="v">{esc(v)}</div><div class="d">{esc(d)}</div></div>'
        for k, v, d in kpis
    )

    # origin split bar
    org_pct = (n_org / total * 100) if total else 0
    seed_pct = 100 - org_pct
    split_bar = (
        f'<div class="splitbar">'
        f'<div class="seg organic" style="width:{org_pct:.2f}%" title="{n_org} organic">'
        f'{("organic " + str(n_org)) if org_pct >= 8 else ""}</div>'
        f'<div class="seg seed" style="width:{seed_pct:.2f}%" title="{n_seed} seed">'
        f'{("seed " + str(n_seed)) if seed_pct >= 8 else ""}</div>'
        f"</div>"
        f'<div class="minilegend">'
        f'<span class="li"><span class="sw" style="background:var(--rc-teal)"></span>'
        f"Organic — {n_org} real problems from engagements</span>"
        f'<span class="li"><span class="sw" style="background:var(--rc-faint)"></span>'
        f"Seed — {n_seed} synthetic starter examples</span></div>"
    )

    seed_dates_str = ", ".join(sorted(seed_dates)) if seed_dates else "none detected"

    # filter option lists
    plugin_opts = "".join(
        f'<option value="{esc(p)}">{esc(p)} ({n})</option>' for p, n in sorted(by_plugin.items())
    )
    scope_opts = "".join(
        f'<option value="{esc(s)}">{esc(s)} ({n})</option>' for s, n in sorted(by_scope.items())
    )

    # table rows — sort organic first, then by plugin then date (deterministic)
    ordered = sorted(records, key=lambda r: (r["origin"] != "organic", r["plugin"], r["contributed_at"], r["scenario_id"]))
    trows = []
    for r in ordered:
        hay = " ".join(
            [r["problem"], r["resolution"], r["plugin"], r["product"], r["scope"], " ".join(r["tags"]), r["scenario_id"]]
        ).lower()
        tagrow = "".join(f'<span class="tag">{esc(t)}</span>' for t in r["tags"][:7])
        tagrow_html = f'<div class="tagrow">{tagrow}</div>' if tagrow else ""
        origin = r["origin"]
        trows.append(
            f'<tr class="r" data-search="{esc(hay)}" data-plugin="{esc(r["plugin"])}" '
            f'data-scope="{esc(r["scope"])}" data-origin="{origin}" '
            f'data-problem="{esc(r["problem"][:80])}" data-date="{esc(r["contributed_at"])}">'
            f'<td><span class="pill {origin}">{esc(origin)}</span></td>'
            f'<td><div class="prob">{esc(shorten(r["problem"]))}</div>{tagrow_html}</td>'
            f'<td><div class="reso">{esc(shorten(r["resolution"]))}</div></td>'
            f'<td>{esc(r["plugin"])}<div class="scope">{esc(r["scope"])}</div></td>'
            f'<td class="meta">{esc(r["contributed_at"] or "—")}<br/>{esc(r["confidence"] or "")}</td>'
            f"</tr>"
        )

    title = "Problems &amp; Resolutions"
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Problems &amp; Resolutions — RavenClaude</title>
<style>
/*__SHARED_TOKENS__*/
{REPORT_CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="rhead">
    <div>
      <h1>{title}</h1>
    </div>
    <div class="stamp">As of {esc(as_of)}<br/>Read from the scenario corpus</div>
  </div>
  <p class="lede">Every problem captured in the scenario bank and how it was resolved — one row per
  scenario, read straight from <code>plugins/*/scenarios/*.md</code>. Use the filters to separate the
  handful of <b>organic</b> problems (from real engagements) from the bulk <b>seed</b> examples.</p>

  <div class="kpis">{kpi_html}</div>

  <div class="dq" role="status">
    <span aria-hidden="true">⚠️</span>
    <div><b>Organic vs. seed.</b> {n_seed} of {total} scenarios are a synthetic <b>seed</b> drop
    (bulk-authored on {esc(seed_dates_str)}) — they inflate the count. Only <b>{n_org}</b> are organic
    contributions from real engagements. Use the <i>Origin</i> filter to see just the real ones.</div>
  </div>

  <div class="grid2">
    <div class="panel">
      <h2>Where the problems come from</h2>
      <p class="sub">Organic (real engagements) vs. the synthetic seed set.</p>
      {split_bar}
    </div>
    <div class="panel">
      <h2>Problems by plugin</h2>
      <p class="sub">How many scenarios each plugin has contributed.</p>
      <div class="barlist">{_bar_rows(by_plugin, total, limit=10)}</div>
    </div>
  </div>

  <div class="toolbar">
    <input id="q" type="search" placeholder="Search problems, resolutions, tags…" aria-label="Search"/>
    <select id="fplugin" aria-label="Filter by plugin"><option value="all">All plugins</option>{plugin_opts}</select>
    <select id="fscope" aria-label="Filter by scope"><option value="all">All scopes</option>{scope_opts}</select>
    <div class="seg" role="group" aria-label="Filter by origin">
      <button data-origin="all" aria-pressed="true">All</button>
      <button data-origin="organic" aria-pressed="false">Organic</button>
      <button data-origin="seed" aria-pressed="false">Seed</button>
    </div>
    <span class="count" id="count"></span>
  </div>

  <div class="panel" style="padding:6px 8px">
    <table class="t">
      <thead><tr>
        <th data-key="origin">Origin <span class="arr"></span></th>
        <th data-key="problem">Problem <span class="arr"></span></th>
        <th>Resolution (what worked)</th>
        <th data-key="plugin">Plugin · scope <span class="arr"></span></th>
        <th data-key="date">Date · conf. <span class="arr"></span></th>
      </tr></thead>
      <tbody id="tbody">
        {"".join(trows)}
      </tbody>
    </table>
    <div id="empty" class="empty hidden">No scenarios match these filters.</div>
  </div>

  <p class="foot">
    Self-contained view — no internet needed. Built by <code>scripts/generate-feedback-report.py</code>
    from <code>plugins/*/scenarios/*.md</code>. It reads the corpus and writes nothing back. Only fields
    that already ship in the committed scenario files are rendered (no env / tenant / auth data added).
    The “as of” date is the newest scenario’s contribution date, so the file is stable between runs.
  </p>
</div>
<script>
{REPORT_JS}
</script>
</body>
</html>
"""
    return page.replace("/*__SHARED_TOKENS__*/", tokens)


def build() -> str:
    records = load_scenarios()
    seed_dates = classify_origin(records)
    tokens = _load_shared_tokens()
    return render(records, seed_dates, tokens)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build the self-contained Problems & Resolutions view from the scenario corpus")
    ap.add_argument("--check", action="store_true", help="fail (exit 1) if the committed feedback-report.html is stale")
    args = ap.parse_args(argv)

    page = build()
    if args.check:
        current = OUT_FILE.read_text(encoding="utf-8") if OUT_FILE.exists() else ""
        if current != page:
            print(
                f"STALE {OUT_FILE.relative_to(REPO_ROOT)} — run scripts/generate-feedback-report.py",
                file=sys.stderr,
            )
            return 1
        print("feedback-report.html fresh")
        return 0
    OUT_FILE.write_text(page, encoding="utf-8")
    n = page.count('class="r"')
    print(f"[ok] wrote {OUT_FILE.relative_to(REPO_ROOT)} ({len(page)//1024} KB, {n} scenarios)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
