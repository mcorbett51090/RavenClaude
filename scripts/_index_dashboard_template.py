# Auto-loaded by generate-index-dashboard.py. Holds the self-contained
# HTML/CSS/JS shell for the redesigned RavenClaude landing dashboard.
#
# Placeholders substituted by the generator:
#   /*__RC_DATA__*/  → embedded JSON data object (window.__RC_DATA__)
#   __GENERATED__    → human-readable generation timestamp
#   __MKT_VERSION__  → marketplace catalog version
#
# Keep this a RAW string (r"""...""") so the JS/CSS braces pass through verbatim.

TEMPLATE = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>RavenClaude — AI Engineering Team Platform</title>
    <meta name="description" content="RavenClaude is a private Claude Code plugin marketplace — a domain-neutral orchestration core plus specialist teams for Microsoft, Salesforce, web, data, finance and compliance. Browse plugins, the specialist roster, and the comfort-posture permission editor." />
    <meta name="color-scheme" content="dark" />
    <meta name="theme-color" content="#0b1120" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="index.html" />
    <!-- Open Graph / social -->
    <meta property="og:type" content="website" />
    <meta property="og:title" content="RavenClaude — AI Engineering Team Platform" />
    <meta property="og:description" content="A private Claude Code plugin marketplace: orchestration core + specialist teams, with a point-and-click comfort-posture permission editor." />
    <meta property="og:site_name" content="RavenClaude" />
    <meta name="twitter:card" content="summary" />
    <style>
      :root {
        --bg: #0b1120;
        --bg-2: #0e1626;
        --surface: #111c30;
        --surface-2: #16243c;
        --surface-3: #1c2e4a;
        --border: rgba(148, 197, 214, 0.14);
        --border-strong: rgba(148, 197, 214, 0.28);
        --text: #eef4f8;
        --muted: #93a4bd;
        --faint: #6b7d97;
        --teal: #2dd4bf;
        --teal-2: #5eead4;
        --teal-dim: #14b8a6;
        --teal-soft: rgba(45, 212, 191, 0.14);
        --teal-glow: rgba(45, 212, 191, 0.40);
        --ok: #34d399;
        --warn: #fbbf24;
        --danger: #fb7185;
        --deny: #fb7185;
        --ask: #fbbf24;
        --allow: #34d399;
        --font-sans: "Inter", ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
        --radius: 14px;
        --radius-sm: 9px;
        --sidebar-w: 264px;
        --sidebar-collapsed: 72px;
        --topbar-h: 64px;
        --shadow: 0 18px 50px -20px rgba(0, 0, 0, 0.65);
        --ring: 0 0 0 3px var(--teal-soft);
      }
      * { box-sizing: border-box; }
      html { scroll-behavior: smooth; }
      body {
        margin: 0;
        font-family: var(--font-sans);
        color: var(--text);
        background:
          radial-gradient(1100px 700px at 100% -10%, rgba(45, 212, 191, 0.10), transparent 60%),
          radial-gradient(900px 600px at -10% 10%, rgba(56, 189, 248, 0.08), transparent 55%),
          var(--bg);
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
        min-height: 100vh;
      }
      a { color: var(--teal-2); text-decoration: none; }
      a:hover { color: var(--teal); }
      h1, h2, h3, h4 { letter-spacing: -0.02em; line-height: 1.15; margin: 0; }
      h1 { font-size: clamp(1.9rem, 4vw, 2.8rem); }
      p { line-height: 1.6; }
      ::selection { background: var(--teal); color: #04121a; }
      :focus-visible { outline: none; box-shadow: var(--ring); border-radius: 8px; }
      button { font-family: inherit; cursor: pointer; }

      /* ---------- Layout shell ---------- */
      .app { display: grid; grid-template-columns: var(--sidebar-w) 1fr; min-height: 100vh; transition: grid-template-columns 0.25s ease; }
      body.sidebar-collapsed .app { grid-template-columns: var(--sidebar-collapsed) 1fr; }

      /* ---------- Sidebar ---------- */
      .sidebar {
        position: sticky; top: 0; height: 100vh;
        background: linear-gradient(180deg, var(--bg-2), var(--bg));
        border-right: 1px solid var(--border);
        display: flex; flex-direction: column;
        overflow: hidden; z-index: 40;
      }
      .brand { display: flex; align-items: center; gap: 12px; padding: 16px 18px; height: var(--topbar-h); border-bottom: 1px solid var(--border); white-space: nowrap; }
      .brand .mark { flex: 0 0 auto; width: 34px; height: 34px; display: grid; place-items: center; border-radius: 10px; background: var(--teal-soft); border: 1px solid var(--border-strong); color: var(--teal-2); box-shadow: 0 0 18px -4px var(--teal-glow); }
      .brand .mark svg { width: 20px; height: 20px; }
      .brand .name { font-weight: 700; font-size: 1.05rem; }
      .brand .name b { color: var(--teal-2); }
      .brand .tag { display: block; font-size: 0.66rem; color: var(--faint); font-weight: 500; letter-spacing: 0.04em; text-transform: uppercase; }
      body.sidebar-collapsed .brand .meta { display: none; }

      .nav { padding: 14px 12px; display: flex; flex-direction: column; gap: 4px; overflow-y: auto; flex: 1; }
      .nav .group-label { font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--faint); padding: 14px 12px 6px; }
      body.sidebar-collapsed .nav .group-label { opacity: 0; }
      .nav a.nav-item {
        display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: var(--radius-sm);
        color: var(--muted); font-weight: 500; font-size: 0.92rem; white-space: nowrap;
        transition: background 0.15s, color 0.15s; position: relative;
      }
      .nav a.nav-item svg { width: 19px; height: 19px; flex: 0 0 auto; }
      .nav a.nav-item:hover { background: var(--surface); color: var(--text); }
      .nav a.nav-item.active { background: var(--teal-soft); color: var(--teal-2); }
      .nav a.nav-item.active::before { content: ""; position: absolute; left: 0; top: 8px; bottom: 8px; width: 3px; border-radius: 3px; background: var(--teal); }
      body.sidebar-collapsed .nav a.nav-item .label { display: none; }
      body.sidebar-collapsed .nav a.nav-item { justify-content: center; }

      .sidebar-foot { padding: 12px; border-top: 1px solid var(--border); font-size: 0.72rem; color: var(--faint); white-space: nowrap; }
      body.sidebar-collapsed .sidebar-foot .detail { display: none; }

      /* ---------- Main ---------- */
      .main { min-width: 0; display: flex; flex-direction: column; }
      .topbar {
        position: sticky; top: 0; z-index: 30; height: var(--topbar-h);
        display: flex; align-items: center; gap: 14px; padding: 0 20px;
        background: rgba(11, 17, 32, 0.82); backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--border);
      }
      .icon-btn { width: 38px; height: 38px; display: grid; place-items: center; border-radius: 10px; background: var(--surface); border: 1px solid var(--border); color: var(--muted); transition: 0.15s; }
      .icon-btn:hover { color: var(--text); border-color: var(--border-strong); background: var(--surface-2); }
      .icon-btn svg { width: 18px; height: 18px; }

      .search { position: relative; flex: 1; max-width: 520px; }
      .search input {
        width: 100%; height: 40px; padding: 0 14px 0 40px; border-radius: 10px;
        background: var(--surface); border: 1px solid var(--border); color: var(--text);
        font-size: 0.9rem; font-family: inherit; transition: 0.15s;
      }
      .search input::placeholder { color: var(--faint); }
      .search input:focus { border-color: var(--teal-dim); background: var(--surface-2); }
      .search .s-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--faint); width: 18px; height: 18px; pointer-events: none; }
      .search kbd { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); font-size: 0.68rem; color: var(--faint); border: 1px solid var(--border); border-radius: 6px; padding: 2px 6px; font-family: var(--font-mono); }
      .search-results {
        position: absolute; top: 48px; left: 0; right: 0; max-height: 60vh; overflow-y: auto;
        background: var(--surface); border: 1px solid var(--border-strong); border-radius: 12px;
        box-shadow: var(--shadow); padding: 6px; display: none;
      }
      .search-results.open { display: block; }
      .search-results .res {
        display: flex; align-items: center; gap: 10px; padding: 9px 10px; border-radius: 8px; color: var(--text); cursor: pointer;
      }
      .search-results .res:hover, .search-results .res.cursor { background: var(--surface-2); }
      .search-results .res .kind { font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--teal-2); border: 1px solid var(--border); border-radius: 999px; padding: 2px 8px; flex: 0 0 auto; }
      .search-results .res .meta { color: var(--faint); font-size: 0.78rem; margin-left: auto; }
      .search-results .empty { padding: 16px; color: var(--faint); text-align: center; font-size: 0.85rem; }

      .topbar .actions { display: flex; align-items: center; gap: 8px; margin-left: auto; }
      .btn {
        display: inline-flex; align-items: center; gap: 8px; padding: 9px 14px; border-radius: 10px;
        font-size: 0.85rem; font-weight: 600; border: 1px solid var(--border); background: var(--surface); color: var(--text);
        transition: 0.15s; white-space: nowrap;
      }
      .btn svg { width: 16px; height: 16px; }
      .btn:hover { border-color: var(--border-strong); background: var(--surface-2); }
      .btn.primary { background: linear-gradient(180deg, var(--teal), var(--teal-dim)); color: #04121a; border-color: transparent; box-shadow: 0 8px 22px -10px var(--teal-glow); }
      .btn.primary:hover { filter: brightness(1.06); }
      .btn.ghost { background: transparent; }
      .hide-sm { }

      /* ---------- Content ---------- */
      .content { padding: 28px clamp(16px, 4vw, 40px) 64px; max-width: 1320px; width: 100%; margin: 0 auto; animation: fade 0.35s ease; }
      @keyframes fade { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
      .page-head { margin-bottom: 24px; }
      .page-head .eyebrow { color: var(--teal-2); font-size: 0.74rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; }
      .page-head p.lede { color: var(--muted); margin-top: 8px; max-width: 70ch; }

      .card { background: linear-gradient(180deg, var(--surface), var(--bg-2)); border: 1px solid var(--border); border-radius: var(--radius); padding: 18px; transition: 0.18s; }
      .card:hover { border-color: var(--border-strong); transform: translateY(-2px); box-shadow: var(--shadow); }
      .grid { display: grid; gap: 16px; }
      .cols-2 { grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); }
      .cols-3 { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
      .cols-4 { grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); }

      /* Hero */
      .hero { position: relative; overflow: hidden; border-radius: 20px; padding: clamp(28px, 5vw, 52px); margin-bottom: 28px;
        background: radial-gradient(700px 360px at 88% -20%, rgba(45,212,191,0.18), transparent 60%), linear-gradient(180deg, var(--surface), var(--bg-2));
        border: 1px solid var(--border); }
      .hero .pill { display: inline-flex; align-items: center; gap: 8px; font-size: 0.74rem; font-weight: 600; color: var(--teal-2); background: var(--teal-soft); border: 1px solid var(--border-strong); padding: 6px 12px; border-radius: 999px; }
      .hero h1 { margin: 18px 0 10px; }
      .hero h1 .accent { background: linear-gradient(90deg, var(--teal-2), var(--teal-dim)); -webkit-background-clip: text; background-clip: text; color: transparent; }
      .hero p { color: var(--muted); max-width: 64ch; font-size: 1.05rem; }
      .hero .hero-cta { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 22px; }

      /* Stat cards */
      .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 28px; }
      .stat { display: flex; flex-direction: column; gap: 4px; }
      .stat .v { font-size: 2.1rem; font-weight: 700; color: var(--teal-2); line-height: 1; }
      .stat .k { color: var(--muted); font-size: 0.86rem; }
      .stat .sub { color: var(--faint); font-size: 0.74rem; }

      /* Action tiles */
      .action-tile { display: flex; gap: 14px; align-items: flex-start; text-align: left; width: 100%; }
      .action-tile .ico { width: 44px; height: 44px; flex: 0 0 auto; border-radius: 12px; display: grid; place-items: center; background: var(--teal-soft); color: var(--teal-2); border: 1px solid var(--border-strong); }
      .action-tile .ico svg { width: 22px; height: 22px; }
      .action-tile .t { font-weight: 600; font-size: 1rem; }
      .action-tile .d { color: var(--muted); font-size: 0.84rem; margin-top: 2px; }

      .section-title { display: flex; align-items: baseline; gap: 12px; margin: 34px 0 14px; }
      .section-title h2 { font-size: 1.3rem; }
      .section-title .hint { color: var(--faint); font-size: 0.82rem; }

      .chip { display: inline-flex; align-items: center; gap: 5px; font-size: 0.72rem; font-weight: 600; padding: 3px 9px; border-radius: 999px; background: var(--surface-2); border: 1px solid var(--border); color: var(--muted); }
      .chip.teal { color: var(--teal-2); border-color: var(--border-strong); background: var(--teal-soft); }
      .tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }

      /* Plugin card */
      .plugin-card { display: flex; flex-direction: column; height: 100%; }
      .plugin-card .pc-head { display: flex; align-items: center; gap: 10px; }
      .plugin-card .pc-head .nm { font-weight: 700; font-size: 1.02rem; }
      .plugin-card .ver { margin-left: auto; font-family: var(--font-mono); font-size: 0.72rem; color: var(--faint); }
      .plugin-card .desc { color: var(--muted); font-size: 0.86rem; margin: 10px 0 0; flex: 1; }
      .plugin-card .metrics { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; font-size: 0.76rem; color: var(--faint); }
      .plugin-card .metrics b { color: var(--teal-2); }
      .plugin-card .pc-foot { display: flex; gap: 8px; margin-top: 14px; }

      /* Marketplace layout */
      .mkt { display: grid; grid-template-columns: 240px 1fr; gap: 22px; align-items: start; }
      .mkt-nav { position: sticky; top: calc(var(--topbar-h) + 20px); display: flex; flex-direction: column; gap: 4px; }
      .mkt-nav button { display: flex; align-items: center; gap: 10px; text-align: left; padding: 10px 12px; border-radius: 10px; background: transparent; border: 1px solid transparent; color: var(--muted); font-size: 0.88rem; font-weight: 500; }
      .mkt-nav button svg { width: 17px; height: 17px; }
      .mkt-nav button:hover { background: var(--surface); color: var(--text); }
      .mkt-nav button.active { background: var(--teal-soft); color: var(--teal-2); border-color: var(--border-strong); }
      .mkt-nav button .count { margin-left: auto; font-size: 0.72rem; color: var(--faint); }
      .mkt-filters { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 18px; align-items: center; }
      .mkt-filters input { flex: 1; min-width: 200px; height: 40px; padding: 0 14px; border-radius: 10px; background: var(--surface); border: 1px solid var(--border); color: var(--text); font-family: inherit; }
      .mkt-filters input:focus { border-color: var(--teal-dim); }

      /* Roster table */
      .roster-controls { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }
      .roster-controls select, .roster-controls input { height: 40px; padding: 0 12px; border-radius: 10px; background: var(--surface); border: 1px solid var(--border); color: var(--text); font-family: inherit; font-size: 0.88rem; }
      .roster-controls input { flex: 1; min-width: 200px; }
      .agent-card .ac-head { display: flex; align-items: center; gap: 10px; }
      .agent-card .ac-head .nm { font-weight: 600; }
      .agent-card .role { margin-left: auto; }
      .agent-card .desc { color: var(--muted); font-size: 0.84rem; margin-top: 8px; }
      .agent-card .trig { margin-top: 10px; font-size: 0.78rem; color: var(--faint); }
      .agent-card .trig code { color: var(--teal-2); background: var(--surface-2); padding: 1px 6px; border-radius: 6px; font-family: var(--font-mono); }

      details.lib { border: 1px solid var(--border); border-radius: 12px; margin-bottom: 10px; background: var(--surface); overflow: hidden; }
      details.lib > summary { list-style: none; cursor: pointer; padding: 14px 16px; display: flex; align-items: center; gap: 10px; font-weight: 600; }
      details.lib > summary::-webkit-details-marker { display: none; }
      details.lib > summary .caret { margin-left: auto; transition: transform 0.2s; color: var(--faint); }
      details.lib[open] > summary .caret { transform: rotate(90deg); }
      details.lib .lib-body { padding: 0 16px 16px; color: var(--muted); font-size: 0.86rem; }
      details.lib .lib-body .pill-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 6px; }

      /* Configuration / posture */
      .config-grid { display: grid; grid-template-columns: 1fr 380px; gap: 22px; align-items: start; }
      .preset-row { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 8px; }
      .preset-btn { padding: 10px 14px; border-radius: 12px; border: 1px solid var(--border); background: var(--surface); color: var(--text); font-weight: 600; font-size: 0.86rem; display: flex; flex-direction: column; align-items: flex-start; gap: 2px; max-width: 230px; text-align: left; }
      .preset-btn small { font-weight: 400; color: var(--faint); font-size: 0.72rem; }
      .preset-btn:hover { border-color: var(--teal-dim); }
      .preset-btn.active { border-color: var(--teal); background: var(--teal-soft); }

      .pcat-group { margin-top: 20px; }
      .pcat-group h4 { font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--faint); margin-bottom: 10px; }
      .pcat { display: flex; align-items: center; gap: 14px; padding: 12px 0; border-bottom: 1px solid var(--border); }
      .pcat .pc-info { min-width: 0; flex: 1; }
      .pcat .pc-info .t { font-weight: 600; font-size: 0.92rem; }
      .pcat .pc-info .d { color: var(--muted); font-size: 0.8rem; margin-top: 2px; }
      .seg { display: inline-flex; border: 1px solid var(--border); border-radius: 10px; overflow: hidden; flex: 0 0 auto; background: var(--bg-2); }
      .seg button { padding: 7px 14px; background: transparent; border: none; color: var(--muted); font-size: 0.8rem; font-weight: 600; transition: 0.12s; }
      .seg button + button { border-left: 1px solid var(--border); }
      .seg button[data-level="deny"].on { background: rgba(251,113,133,0.18); color: var(--deny); }
      .seg button[data-level="ask"].on { background: rgba(251,191,36,0.18); color: var(--ask); }
      .seg button[data-level="allow"].on { background: rgba(52,211,153,0.18); color: var(--allow); }

      .yaml-panel { position: sticky; top: calc(var(--topbar-h) + 20px); }
      .yaml-panel pre { background: #060c16; border: 1px solid var(--border); border-radius: 12px; padding: 14px; overflow: auto; max-height: 460px; font-family: var(--font-mono); font-size: 0.76rem; color: #cfe7e2; line-height: 1.5; }
      .yaml-panel .yp-head { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
      .toggle-row { display: flex; align-items: center; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border); }
      .switch { position: relative; width: 46px; height: 26px; flex: 0 0 auto; }
      .switch input { opacity: 0; width: 0; height: 0; }
      .switch .track { position: absolute; inset: 0; background: var(--surface-3); border-radius: 999px; transition: 0.2s; border: 1px solid var(--border); }
      .switch .track::before { content: ""; position: absolute; width: 18px; height: 18px; left: 3px; top: 3px; background: var(--muted); border-radius: 50%; transition: 0.2s; }
      .switch input:checked + .track { background: var(--teal-soft); border-color: var(--teal); }
      .switch input:checked + .track::before { transform: translateX(20px); background: var(--teal-2); }

      .floor-list { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
      .floor-list code { font-family: var(--font-mono); font-size: 0.72rem; color: var(--danger); background: rgba(251,113,133,0.10); border: 1px solid rgba(251,113,133,0.25); padding: 2px 8px; border-radius: 6px; }

      .callout { border: 1px solid var(--border-strong); border-radius: 12px; padding: 14px 16px; background: var(--teal-soft); color: var(--text); font-size: 0.86rem; display: flex; gap: 12px; }
      .callout svg { width: 20px; height: 20px; color: var(--teal-2); flex: 0 0 auto; margin-top: 2px; }

      .toast { position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%) translateY(20px); background: var(--surface-3); border: 1px solid var(--teal); color: var(--text); padding: 12px 18px; border-radius: 10px; font-size: 0.86rem; box-shadow: var(--shadow); opacity: 0; pointer-events: none; transition: 0.25s; z-index: 90; }
      .toast.show { opacity: 1; transform: translateX(-50%) translateY(0); }

      .empty-state { text-align: center; padding: 60px 20px; color: var(--faint); }
      .activity-item { display: flex; gap: 12px; align-items: flex-start; padding: 12px 0; border-bottom: 1px solid var(--border); }
      .activity-item .dot { width: 9px; height: 9px; border-radius: 50%; background: var(--teal); margin-top: 6px; flex: 0 0 auto; box-shadow: 0 0 10px var(--teal-glow); }
      .activity-item .when { color: var(--faint); font-size: 0.76rem; margin-left: auto; white-space: nowrap; }

      .scrim { position: fixed; inset: 0; background: rgba(4,8,16,0.6); backdrop-filter: blur(2px); z-index: 35; opacity: 0; pointer-events: none; transition: 0.2s; }
      body.mobile-nav-open .scrim { opacity: 1; pointer-events: auto; }

      /* ---------- Responsive ---------- */
      @media (max-width: 1020px) {
        .config-grid { grid-template-columns: 1fr; }
        .yaml-panel { position: static; }
        .mkt { grid-template-columns: 1fr; }
        .mkt-nav { position: static; flex-direction: row; flex-wrap: wrap; }
      }
      @media (max-width: 820px) {
        .app { grid-template-columns: 1fr !important; }
        .sidebar { position: fixed; left: 0; top: 0; width: var(--sidebar-w); transform: translateX(-100%); transition: transform 0.25s ease; box-shadow: var(--shadow); }
        body.mobile-nav-open .sidebar { transform: translateX(0); }
        body.sidebar-collapsed .nav a.nav-item .label,
        body.sidebar-collapsed .brand .meta { display: revert; }
        .desktop-collapse { display: none; }
        .hide-sm { display: none; }
        .search kbd { display: none; }
      }
      @media (min-width: 821px) { .mobile-only { display: none; } }
      @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; scroll-behavior: auto; } }
    </style>
  </head>
  <body>
    <div class="scrim" id="scrim" aria-hidden="true"></div>
    <div class="app">
      <!-- ======================= SIDEBAR ======================= -->
      <aside class="sidebar" id="sidebar">
        <div class="brand">
          <span class="mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M3 11l9-7 9 7v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 21v-7h6v7" stroke="currentColor"/></svg>
          </span>
          <span class="meta">
            <span class="name">Raven<b>Claude</b></span>
            <span class="tag">Engineering Team Platform</span>
          </span>
        </div>
        <nav class="nav" id="primary-nav" aria-label="Primary"></nav>
        <div class="sidebar-foot">
          <div>v<span id="foot-version">__MKT_VERSION__</span></div>
          <div class="detail">Updated __GENERATED__</div>
        </div>
      </aside>

      <!-- ======================= MAIN ======================= -->
      <div class="main">
        <header class="topbar">
          <button class="icon-btn mobile-only" id="mobile-toggle" aria-label="Open navigation">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18M3 12h18M3 18h18"/></svg>
          </button>
          <button class="icon-btn desktop-collapse" id="collapse-toggle" aria-label="Collapse sidebar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 4v16M4 7l-2 5 2 5" /><rect x="3" y="4" width="18" height="16" rx="2"/></svg>
          </button>
          <div class="search" id="search">
            <svg class="s-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
            <input type="search" id="search-input" placeholder="Search plugins, specialists, skills…" aria-label="Search" autocomplete="off" />
            <kbd>/</kbd>
            <div class="search-results" id="search-results" role="listbox"></div>
          </div>
          <div class="actions">
            <a class="btn ghost hide-sm" href="repo-guide.html"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>Repo Guide</a>
            <a class="btn primary" href="#/marketplace"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v4H3z"/><path d="M5 7v12h14V7"/><path d="M9 11h6"/></svg>Browse Plugins</a>
          </div>
        </header>
        <main class="content" id="view" tabindex="-1"></main>
      </div>
    </div>
    <div class="toast" id="toast" role="status" aria-live="polite"></div>

    <script>
      window.__RC_DATA__ = /*__RC_DATA__*/;
    </script>
    <script>
      "use strict";
      const D = window.__RC_DATA__;
      const $ = (s, r = document) => r.querySelector(s);
      const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
      const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
      const byName = (n) => D.plugins.find((p) => p.name === n);

      /* ---------------- Icons ---------------- */
      const ICONS = {
        home: '<path d="M3 11l9-7 9 7v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
        team: '<circle cx="9" cy="8" r="3"/><path d="M2 20c0-3.3 3.1-5 7-5s7 1.7 7 5"/><path d="M16 5a3 3 0 0 1 0 6"/><path d="M22 20c0-2.4-1.5-4-4-4.5"/>',
        market: '<path d="M3 3h18v4H3z"/><path d="M5 7v12h14V7"/><path d="M9 11h6"/>',
        config: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09a1.65 1.65 0 0 0-1.08-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09a1.65 1.65 0 0 0 1.51-1.08 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
        resources: '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
        hub: '<circle cx="12" cy="12" r="2.5"/><circle cx="5" cy="5" r="2"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="M10.2 10.2 6.5 6.5M13.8 10.2l3.7-3.7M10.2 13.8l-3.7 3.7M13.8 13.8l3.7 3.7"/>',
        windows: '<path d="M3 5.5 10.5 4.5v7H3zM10.5 4.3 21 3v8.5H10.5zM3 12.5h7.5v7L3 18.5zM10.5 12.5H21V21l-10.5-1.5z"/>',
        building: '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 7h.01M15 7h.01M9 11h.01M15 11h.01M9 15h.01M15 15h.01M10 21v-3h4v3"/>',
        palette: '<path d="M12 22a10 10 0 1 1 0-20 8 8 0 0 1 8 8c0 2.2-1.8 3-4 3h-1a2 2 0 0 0-1 3.7A2 2 0 0 1 12 22z"/><circle cx="7.5" cy="10.5" r="1"/><circle cx="12" cy="7.5" r="1"/><circle cx="16.5" cy="10.5" r="1"/>',
        chart: '<path d="M3 3v18h18"/><rect x="7" y="11" width="3" height="6"/><rect x="12" y="7" width="3" height="10"/><rect x="17" y="13" width="3" height="4"/>',
        shield: '<path d="M12 2 4 5v6c0 5 3.4 8.5 8 11 4.6-2.5 8-6 8-11V5z"/><path d="m9 12 2 2 4-4"/>',
        sparkle: '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
        rocket: '<path d="M4.5 16.5c-1.5 1.3-2 5-2 5s3.7-.5 5-2c.7-.8.7-2 0-2.8a2 2 0 0 0-3 .2z"/><path d="M12 15l-3-3a22 22 0 0 1 8-10c2 0 4 2 4 4a22 22 0 0 1-10 8z"/><path d="M9 12H4s.5-3 2-4 5 0 5 0M12 15v5s3-.5 4-2 0-5 0-5"/>',
        sliders: '<path d="M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6"/>',
        book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
        git: '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="9" r="3"/><path d="M6 9v6M18 12c0 3-4 3-6 3"/>',
        copy: '<rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/>',
        download: '<path d="M12 3v12m0 0 4-4m-4 4-4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/>',
        spark: '<path d="M13 2 4 14h7l-1 8 9-12h-7z"/>',
        info: '<circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v4h1"/>',
        plus: '<path d="M12 5v14M5 12h14"/>',
        tree: '<circle cx="12" cy="4" r="2"/><circle cx="5" cy="20" r="2"/><circle cx="19" cy="20" r="2"/><path d="M12 6v4M12 10 5 18M12 10l7 8"/>',
        check: '<path d="m20 6-11 11-5-5"/>',
        external: '<path d="M15 3h6v6M10 14 21 3M21 14v5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5"/>',
      };
      const svg = (name, cls = "") => `<svg ${cls ? 'class="' + cls + '" ' : ""}viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICONS[name] || ICONS.sparkle}</svg>`;

      /* ---------------- Sidebar nav ---------------- */
      const NAV = [
        { id: "home", label: "Home", icon: "home" },
        { id: "team", label: "Team", icon: "team" },
        { id: "marketplace", label: "Marketplace", icon: "market" },
        { id: "configuration", label: "Configuration", icon: "config" },
        { id: "resources", label: "Resources", icon: "resources" },
      ];
      function renderNav(active) {
        $("#primary-nav").innerHTML =
          '<div class="group-label">Platform</div>' +
          NAV.map((n) => `<a class="nav-item${n.id === active ? " active" : ""}" href="#/${n.id}" data-nav="${n.id}"${n.id === active ? ' aria-current="page"' : ""}>${svg(n.icon)}<span class="label">${n.label}</span></a>`).join("");
      }

      /* ---------------- Toast ---------------- */
      let toastT;
      function toast(msg) {
        const t = $("#toast");
        t.textContent = msg;
        t.classList.add("show");
        clearTimeout(toastT);
        toastT = setTimeout(() => t.classList.remove("show"), 2400);
      }
      function copyText(text, label) {
        navigator.clipboard?.writeText(text).then(
          () => toast((label || "Copied") + " to clipboard"),
          () => toast("Copy failed — select & copy manually")
        );
      }
      window.__copy = copyText;

      /* ---------------- HOME ---------------- */
      function viewHome() {
        const s = D.stats;
        const qa = D.quick_actions.map((a) => {
          const href = a.route || a.href || "#/home";
          const onclick = a.command ? ` onclick="window.__copy('${esc(a.command)}','Command ${esc(a.command)}'); return ${a.href || a.route ? "true" : "false"};"` : "";
          const tag = a.href ? "a" : a.route ? "a" : "button";
          const attrs = a.href ? `href="${esc(a.href)}"` : a.route ? `href="${esc(a.route)}"` : "type=\"button\"";
          return `<${tag} class="card"${onclick} ${attrs} style="display:block">
            <div class="action-tile"><span class="ico">${svg(a.icon)}</span><span><span class="t">${esc(a.label)}</span><span class="d">${esc(a.desc)}</span></span></div>
          </${tag}>`;
        }).join("");

        const featured = D.featured.map((f) => {
          const plugins = f.plugins.map(byName).filter(Boolean);
          const tags = plugins.map((p) => `<span class="chip teal">${esc(p.label)}</span>`).join("");
          const total = plugins.reduce((n, p) => n + p.counts.agents, 0);
          return `<div class="card"><div style="font-weight:700">${esc(f.title)}</div>
            <p class="desc" style="color:var(--muted);font-size:.86rem;margin:8px 0 0">${esc(f.blurb)}</p>
            <div class="tags">${tags}</div>
            <div class="metrics" style="margin-top:12px;font-size:.76rem;color:var(--faint)"><span><b style="color:var(--teal-2)">${total}</b> specialists combined</span></div>
            <div class="pc-foot" style="margin-top:14px"><a class="btn" href="#/marketplace">View in marketplace</a></div></div>`;
        }).join("");

        const activity = [
          { t: `Marketplace catalog at v${D.marketplace_version} — ${s.plugins} plugins published`, w: D.generated_date },
          { t: `Dashboard regenerated from live repo data`, w: D.generated_date },
          { t: `${s.specialists} specialist agents across the roster`, w: D.generated_date },
        ].map((a) => `<div class="activity-item"><span class="dot"></span><span>${esc(a.t)}</span><span class="when">${esc(a.w)}</span></div>`).join("");

        $("#view").innerHTML = `
          <section class="hero">
            <span class="pill">${svg("spark")} Private Claude Code marketplace · v${esc(D.marketplace_version)}</span>
            <h1>The <span class="accent">AI Engineering Team</span> Platform</h1>
            <p>A domain-neutral orchestration core plus ${s.plugins - 1} specialist teams — Microsoft, Salesforce, web, data, finance and compliance — wired into Claude Code with a point-and-click permission posture you control.</p>
            <div class="hero-cta">
              <a class="btn primary" href="#/marketplace">${svg("market")} Explore the Marketplace</a>
              <a class="btn" href="#/configuration">${svg("sliders")} Tune Comfort Posture</a>
              <a class="btn ghost" href="repo-guide.html">${svg("book")} Full Repo Guide</a>
            </div>
          </section>

          <div class="stats">
            <div class="card stat"><span class="v">${s.plugins}</span><span class="k">Active Plugins</span><span class="sub">in the catalog</span></div>
            <div class="card stat"><span class="v">${s.specialists}</span><span class="k">Specialists</span><span class="sub">agents on the roster</span></div>
            <div class="card stat"><span class="v">${s.hooks}</span><span class="k">Active Hooks</span><span class="sub">gates & guardrails</span></div>
            <div class="card stat"><span class="v">${s.skills}</span><span class="k">Skills</span><span class="sub">invokable capabilities</span></div>
          </div>

          <div class="section-title"><h2>Quick actions</h2><span class="hint">one click to the things you do most</span></div>
          <div class="grid cols-4">${qa}</div>

          <div class="section-title"><h2>Featured plugin combinations</h2><span class="hint">teams that work well together</span></div>
          <div class="grid cols-2">${featured}</div>

          <div class="section-title"><h2>Recent activity</h2><span class="hint">generated snapshot</span></div>
          <div class="card">${activity}<p style="color:var(--faint);font-size:.8rem;margin:14px 0 0">Live activity (PR events, posture changes) streams here once wired to the session feed.</p></div>
        `;
      }

      /* ---------------- TEAM ---------------- */
      const allAgents = () => D.plugins.flatMap((p) => p.agents.map((a) => ({ ...a, plugin: p.name, pluginLabel: p.label, domain: p.category_label })));
      function viewTeam() {
        const agents = allAgents();
        const domains = [...new Set(agents.map((a) => a.domain))].sort();
        $("#view").innerHTML = `
          <div class="page-head"><span class="eyebrow">The Team</span><h1>Specialist roster &amp; collaboration</h1>
            <p class="lede">${agents.length} agents across ${D.plugins.length} plugins. The Team Lead dispatches; specialists execute. Filter the roster, browse the skills &amp; hooks library, and review the rules that govern hand-offs.</p></div>

          <div class="section-title"><h2>Agents roster</h2><span class="hint" id="roster-count"></span></div>
          <div class="roster-controls">
            <input type="search" id="roster-q" placeholder="Filter by name or description…" aria-label="Filter agents" />
            <select id="roster-domain" aria-label="Filter by domain"><option value="">All domains</option>${domains.map((d) => `<option>${esc(d)}</option>`).join("")}</select>
            <select id="roster-plugin" aria-label="Filter by plugin"><option value="">All plugins</option>${D.plugins.map((p) => `<option value="${esc(p.name)}">${esc(p.label)}</option>`).join("")}</select>
          </div>
          <div class="grid cols-3" id="roster-grid"></div>

          <div class="section-title"><h2>Dispatch playbooks</h2><span class="hint">how work is routed</span></div>
          <div class="grid cols-3">
            ${[
              { t: "Route by blast radius", d: "The Team Lead traverses the decision tree and picks the smaller-blast-radius specialist rather than keyword-matching the request to a method." },
              { t: "Escalate across domains", d: "Cross-domain or security-sensitive work escalates to ravenclaude-core (architect / security-reviewer) before a specialist proceeds." },
              { t: "Hand off structured", d: "Every hand-off carries the Structured Output Protocol envelope — summary, decisions, artifacts, open questions — so the next agent has full context." },
            ].map((x) => `<div class="card"><div style="display:flex;gap:10px;align-items:center"><span class="ico" style="width:36px;height:36px;border-radius:10px;display:grid;place-items:center;background:var(--teal-soft);color:var(--teal-2);border:1px solid var(--border-strong)">${svg("tree")}</span><b>${esc(x.t)}</b></div><p style="color:var(--muted);font-size:.85rem;margin:10px 0 0">${esc(x.d)}</p></div>`).join("")}
          </div>

          <div class="section-title"><h2>Skills &amp; hooks library</h2><span class="hint">per plugin · ${D.stats.skills} skills · ${D.stats.hooks} hooks</span></div>
          <div id="lib-list"></div>

          <div class="section-title"><h2>Collaboration rules</h2><span class="hint">the constitution, summarized</span></div>
          <div class="grid cols-2">
            ${D.collab_rules.map((r) => `<div class="card"><div style="display:flex;gap:10px;align-items:center"><span style="color:var(--teal-2)">${svg("check")}</span><b>${esc(r.title)}</b></div><p style="color:var(--muted);font-size:.86rem;margin:10px 0 0">${esc(r.body)}</p></div>`).join("")}
          </div>
        `;
        // Library
        $("#lib-list").innerHTML = D.plugins.filter((p) => p.counts.skills || p.counts.hooks || p.counts.commands).map((p) => `
          <details class="lib"><summary>${esc(p.label)} <span class="chip teal" style="margin-left:4px">${p.counts.skills} skills</span> <span class="chip">${p.counts.hooks} hooks</span> <span class="chip">${p.counts.commands} commands</span><span class="caret">${svg("tree")}</span></summary>
            <div class="lib-body">${esc(p.short)}<div class="pill-row">${p.keywords.map((k) => `<span class="chip">${esc(k)}</span>`).join("")}</div></div></details>`).join("");

        // Roster filtering
        const grid = $("#roster-grid");
        function renderRoster() {
          const q = $("#roster-q").value.toLowerCase().trim();
          const dom = $("#roster-domain").value;
          const plg = $("#roster-plugin").value;
          const list = agents.filter((a) =>
            (!dom || a.domain === dom) && (!plg || a.plugin === plg) &&
            (!q || a.label.toLowerCase().includes(q) || (a.description || "").toLowerCase().includes(q) || a.name.toLowerCase().includes(q)));
          $("#roster-count").textContent = `${list.length} of ${agents.length}`;
          grid.innerHTML = list.length ? list.map((a) => `
            <div class="card agent-card">
              <div class="ac-head"><span class="nm">${esc(a.label)}</span><span class="chip teal role">${esc(a.pluginLabel)}</span></div>
              <div class="desc">${esc(a.description || "Specialist agent.")}</div>
              ${a.triggers && a.triggers.length ? `<div class="trig">Try: <code>${esc(a.triggers[0])}</code></div>` : ""}
            </div>`).join("") : `<div class="empty-state">No agents match those filters.</div>`;
        }
        ["roster-q", "roster-domain", "roster-plugin"].forEach((id) => { $("#" + id).addEventListener("input", renderRoster); });
        renderRoster();
      }

      /* ---------------- MARKETPLACE ---------------- */
      let mktState = { cat: "all", q: "" };
      function viewMarketplace(catId) {
        mktState.cat = catId || "all";
        const cats = D.categories;
        const counts = {};
        D.plugins.forEach((p) => { counts[p.category] = (counts[p.category] || 0) + 1; });
        const navBtns = `<button data-cat="all" class="${mktState.cat === "all" ? "active" : ""}">${svg("market")} All plugins <span class="count">${D.plugins.length}</span></button>` +
          cats.map((c) => `<button data-cat="${c.id}" class="${mktState.cat === c.id ? "active" : ""}">${svg(c.icon)} ${esc(c.label)} <span class="count">${counts[c.id] || 0}</span></button>`).join("");

        $("#view").innerHTML = `
          <div class="page-head"><span class="eyebrow">Marketplace</span><h1>Browse the plugin catalog</h1>
            <p class="lede">${D.plugins.length} opinionated plugins, grouped by domain. Each ships specialist agents, skills, and a knowledge bank. Pick a category or search across everything.</p></div>
          <div class="mkt-filters">
            <input type="search" id="mkt-q" placeholder="Search plugins by name, description or technology…" value="${esc(mktState.q)}" aria-label="Search plugins" />
          </div>
          <div class="mkt">
            <nav class="mkt-nav" id="mkt-nav" aria-label="Plugin categories">${navBtns}</nav>
            <div id="mkt-grid"></div>
          </div>`;

        function pluginCard(p) {
          const reqs = (p.requires || []).length ? `<span class="chip">requires core</span>` : "";
          return `<div class="card plugin-card">
            <div class="pc-head"><span class="ico" style="width:34px;height:34px;border-radius:9px;display:grid;place-items:center;background:var(--teal-soft);color:var(--teal-2);border:1px solid var(--border-strong)">${svg((cats.find((c) => c.id === p.category) || {}).icon || "sparkle")}</span><span class="nm">${esc(p.label)}</span><span class="ver">v${esc(p.version)}</span></div>
            <p class="desc">${esc(p.short)}</p>
            <div class="metrics"><span><b>${p.counts.agents}</b> specialists</span><span><b>${p.counts.skills}</b> skills</span><span><b>${p.counts.knowledge}</b> knowledge docs</span></div>
            <div class="tags">${p.keywords.slice(0, 5).map((k) => `<span class="chip">${esc(k)}</span>`).join("")} ${reqs}</div>
            <div class="pc-foot"><button class="btn primary" type="button" onclick="window.__copy('/plugin install ${esc(p.name)}@ravenclaude','Install command')">${svg("plus")} Add to Project</button><button class="btn" type="button" onclick="window.__openPlugin('${esc(p.name)}')">Details</button></div>
          </div>`;
        }
        function renderGrid() {
          const q = mktState.q.toLowerCase().trim();
          let list = D.plugins.filter((p) => mktState.cat === "all" || p.category === mktState.cat);
          if (q) list = list.filter((p) => (p.label + " " + p.description + " " + p.keywords.join(" ")).toLowerCase().includes(q));
          const cat = cats.find((c) => c.id === mktState.cat);
          const head = cat ? `<div class="callout" style="margin-bottom:18px">${svg("info")}<span><b>${esc(cat.label)}</b> — ${esc(cat.blurb)}</span></div>` : "";
          $("#mkt-grid").innerHTML = head + (list.length ? `<div class="grid cols-2">${list.map(pluginCard).join("")}</div>` : `<div class="empty-state">No plugins match “${esc(mktState.q)}”.</div>`);
        }
        $("#mkt-nav").addEventListener("click", (e) => {
          const b = e.target.closest("button"); if (!b) return;
          mktState.cat = b.dataset.cat;
          $$("#mkt-nav button").forEach((x) => x.classList.toggle("active", x === b));
          if (mktState.cat === "all") { history.replaceState(null, "", "#/marketplace"); } else { history.replaceState(null, "", "#/marketplace/" + mktState.cat); }
          renderGrid();
        });
        $("#mkt-q").addEventListener("input", (e) => { mktState.q = e.target.value; renderGrid(); });
        renderGrid();
      }
      window.__openPlugin = function (name) {
        const p = byName(name); if (!p) return;
        const cats = D.categories;
        const agents = p.agents.map((a) => `<div class="card agent-card" style="padding:14px"><div class="ac-head"><span class="nm">${esc(a.label)}</span></div><div class="desc">${esc(a.description || "")}</div>${a.triggers && a.triggers[0] ? `<div class="trig">Try: <code>${esc(a.triggers[0])}</code></div>` : ""}</div>`).join("");
        $("#view").innerHTML = `
          <a class="btn ghost" href="#/marketplace/${p.category}" style="margin-bottom:18px">← Back to ${esc((cats.find((c) => c.id === p.category) || {}).label || "Marketplace")}</a>
          <div class="page-head"><span class="eyebrow">${esc(p.category_label)}</span><h1>${esc(p.label)} <span style="font-family:var(--font-mono);font-size:1rem;color:var(--faint)">v${esc(p.version)}</span></h1>
            <p class="lede">${esc(p.description)}</p>
            <div class="hero-cta" style="margin-top:16px"><button class="btn primary" type="button" onclick="window.__copy('/plugin install ${esc(p.name)}@ravenclaude','Install command')">${svg("plus")} Copy install command</button></div></div>
          <div class="stats">
            <div class="card stat"><span class="v">${p.counts.agents}</span><span class="k">Specialists</span></div>
            <div class="card stat"><span class="v">${p.counts.skills}</span><span class="k">Skills</span></div>
            <div class="card stat"><span class="v">${p.counts.templates}</span><span class="k">Templates</span></div>
            <div class="card stat"><span class="v">${p.counts.knowledge}</span><span class="k">Knowledge docs</span></div>
          </div>
          ${agents ? `<div class="section-title"><h2>Specialists</h2></div><div class="grid cols-3">${agents}</div>` : ""}
          <div class="tags" style="margin-top:20px">${p.keywords.map((k) => `<span class="chip">${esc(k)}</span>`).join("")}</div>`;
        $("#view").focus();
        window.scrollTo({ top: 0, behavior: "smooth" });
      };

      /* ---------------- CONFIGURATION ---------------- */
      const posture = { levels: {}, design_checkins: true, global_default: "ask", activePreset: "client_delivery" };
      function applyPreset(id) {
        const pr = D.posture.presets.find((p) => p.id === id);
        if (!pr) return;
        posture.levels = { ...pr.levels };
        posture.design_checkins = pr.design_checkins;
        posture.global_default = pr.global_default;
        posture.activePreset = id;
      }
      function postureYaml() {
        const lines = ["# Generated by the RavenClaude comfort-posture editor", "# Drop into .ravenclaude/comfort-posture.yaml, then run apply-comfort-posture.py", "schema_version: 5", "", `design_checkins: ${posture.design_checkins}`, `global_default: ${posture.global_default}`, "", "security_deny:"];
        D.posture.security_floor.forEach((r) => lines.push(`  - ${JSON.stringify(r)}`));
        lines.push("", "categories:");
        D.posture.categories.forEach((c) => {
          const lvl = posture.levels[c.id] || posture.global_default;
          lines.push(`  ${c.id}:`, "    user: inherit", "    local: inherit", `    project: ${lvl}`);
        });
        return lines.join("\n");
      }
      function viewConfiguration() {
        if (!Object.keys(posture.levels).length) applyPreset(posture.activePreset);
        const groups = {};
        D.posture.categories.forEach((c) => { (groups[c.group] = groups[c.group] || []).push(c); });
        const presetRow = D.posture.presets.map((p) => `<button class="preset-btn${p.id === posture.activePreset ? " active" : ""}" data-preset="${p.id}"><span>${esc(p.label)}</span><small>${esc(p.blurb)}</small></button>`).join("");
        const groupHtml = Object.entries(groups).map(([g, cats]) => `
          <div class="pcat-group"><h4>${esc(g)}</h4>${cats.map((c) => `
            <div class="pcat" data-cat="${c.id}">
              <div class="pc-info"><div class="t">${esc(c.title)}</div><div class="d">${esc(c.description)}${c.recommended ? ` · <span style="color:var(--teal-2)">recommended: ${esc(c.recommended)}</span>` : ""}</div></div>
              <div class="seg" role="group" aria-label="${esc(c.title)} level">${D.posture.levels.map((lv) => `<button type="button" data-level="${lv}" data-cat="${c.id}">${lv}</button>`).join("")}</div>
            </div>`).join("")}</div>`).join("");

        $("#view").innerHTML = `
          <div class="page-head"><span class="eyebrow">Configuration</span><h1>Comfort posture &amp; environment</h1>
            <p class="lede">Set how much your agents do without asking — per category, on a deny / ask / allow scale. Start from a profile, fine-tune, then copy the generated <code>comfort-posture.yaml</code>. The always-on security floor can never be relaxed.</p></div>

          <div class="callout" style="margin-bottom:20px">${svg("info")}<span>This editor produces the <b>project-layer</b> baseline. For the full per-layer (user / local / project) editor with live writes to <code>.claude/settings.json</code>, open the deep dashboard via <code>/dashboard</code> or <a href="plugins/ravenclaude-core/dashboard.html">dashboard.html</a>.</span></div>

          <div class="section-title"><h2>Preset profiles</h2><span class="hint">a starting point — tune below</span></div>
          <div class="preset-row" id="preset-row">${presetRow}</div>

          <div class="config-grid">
            <div>
              <div class="toggle-row"><label class="switch"><input type="checkbox" id="design-checkins" ${posture.design_checkins ? "checked" : ""}><span class="track"></span></label><div><div style="font-weight:600">Design check-ins</div><div style="color:var(--muted);font-size:.82rem">Pause for architectural decisions before implementing them.</div></div></div>
              <div class="toggle-row"><div style="font-weight:600;min-width:120px">Global default</div><div class="seg" id="global-default" role="group" aria-label="Global default level">${D.posture.levels.map((lv) => `<button type="button" data-level="${lv}">${lv}</button>`).join("")}</div><div style="color:var(--muted);font-size:.82rem">Fallback for any category left unset.</div></div>
              ${groupHtml}
              <div class="section-title"><h2>Always-on security floor</h2><span class="hint">layer-independent · never relaxed</span></div>
              <div class="floor-list">${D.posture.security_floor.map((r) => `<code>${esc(r)}</code>`).join("")}</div>
            </div>
            <div class="yaml-panel">
              <div class="yp-head">${svg("sliders")}<b>comfort-posture.yaml</b></div>
              <pre id="yaml-out"></pre>
              <div class="pc-foot" style="margin-top:12px"><button class="btn primary" type="button" id="copy-yaml">${svg("copy")} Copy</button><button class="btn" type="button" id="dl-yaml">${svg("download")} Download</button></div>
              <div class="section-title" style="margin-top:24px"><h2 style="font-size:1.05rem">Plugin activation</h2></div>
              <div id="plugin-toggles"></div>
            </div>
          </div>

          <div class="section-title"><h2>Environment context</h2><span class="hint">discovered at session start</span></div>
          <div class="grid cols-2">
            <div class="card"><b>Network policy</b><p style="color:var(--muted);font-size:.85rem;margin:8px 0 0">Outbound access is governed by the environment's network policy chosen at creation. See the <a href="https://code.claude.com/docs/en/claude-code-on-the-web" target="_blank" rel="noopener">Claude Code on the web docs ${svg("external")}</a>.</p></div>
            <div class="card"><b>Run environment discovery</b><p style="color:var(--muted);font-size:.85rem;margin:8px 0 0">Map which credentials your environment can reach with the <code>environment-discovery</code> skill, then record it in <code>.ravenclaude/environment-context.md</code>.</p></div>
          </div>`;

        const yamlOut = $("#yaml-out");
        function refresh() {
          // segmented states
          $$(".pcat .seg button").forEach((b) => b.classList.toggle("on", posture.levels[b.dataset.cat] === b.dataset.level));
          $$("#global-default button").forEach((b) => b.classList.toggle("on", posture.global_default === b.dataset.level));
          $$("#preset-row .preset-btn").forEach((b) => b.classList.toggle("active", b.dataset.preset === posture.activePreset));
          $("#design-checkins").checked = posture.design_checkins;
          yamlOut.textContent = postureYaml();
        }
        $("#preset-row").addEventListener("click", (e) => { const b = e.target.closest(".preset-btn"); if (!b) return; applyPreset(b.dataset.preset); refresh(); toast(`Applied “${b.querySelector("span").textContent}” profile`); });
        $$(".pcat .seg button").forEach((b) => b.addEventListener("click", () => { posture.levels[b.dataset.cat] = b.dataset.level; posture.activePreset = "custom"; refresh(); }));
        $$("#global-default button").forEach((b) => b.addEventListener("click", () => { posture.global_default = b.dataset.level; refresh(); }));
        $("#design-checkins").addEventListener("change", (e) => { posture.design_checkins = e.target.checked; refresh(); });
        $("#copy-yaml").addEventListener("click", () => copyText(postureYaml(), "comfort-posture.yaml"));
        $("#dl-yaml").addEventListener("click", () => {
          const blob = new Blob([postureYaml()], { type: "text/yaml" });
          const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "comfort-posture.yaml"; a.click(); URL.revokeObjectURL(a.href); toast("Downloaded comfort-posture.yaml");
        });
        $("#plugin-toggles").innerHTML = D.plugins.slice().sort((a, b) => a.label.localeCompare(b.label)).map((p) => `
          <div class="toggle-row" style="padding:9px 0"><label class="switch"><input type="checkbox" ${p.name === "ravenclaude-core" ? "checked disabled" : "checked"}><span class="track"></span></label><div style="min-width:0"><div style="font-weight:600;font-size:.9rem">${esc(p.label)}</div><div style="color:var(--faint);font-size:.74rem">v${esc(p.version)}${p.name === "ravenclaude-core" ? " · required" : ""}</div></div></div>`).join("");
        refresh();
      }

      /* ---------------- RESOURCES ---------------- */
      function viewResources() {
        const totalTemplates = D.plugins.reduce((n, p) => n + p.counts.templates, 0);
        const totalKnowledge = D.plugins.reduce((n, p) => n + p.counts.knowledge, 0);
        const templateCards = D.plugins.filter((p) => p.counts.templates).sort((a, b) => b.counts.templates - a.counts.templates).map((p) => `
          <div class="card"><div style="display:flex;align-items:center;gap:8px"><span style="color:var(--teal-2)">${svg("book")}</span><b>${esc(p.label)}</b><span class="ver" style="margin-left:auto;font-family:var(--font-mono);font-size:.72rem;color:var(--faint)">${p.counts.templates} templates</span></div><p style="color:var(--muted);font-size:.82rem;margin:8px 0 0">${esc(p.short)}</p></div>`).join("");
        const treeCards = D.plugins.filter((p) => p.counts.knowledge).sort((a, b) => b.counts.knowledge - a.counts.knowledge).slice(0, 9).map((p) => `
          <div class="card"><div style="display:flex;align-items:center;gap:8px"><span style="color:var(--teal-2)">${svg("tree")}</span><b>${esc(p.label)}</b><span class="ver" style="margin-left:auto;font-family:var(--font-mono);font-size:.72rem;color:var(--faint)">${p.counts.knowledge} docs</span></div><p style="color:var(--muted);font-size:.82rem;margin:8px 0 0">Citation-grounded knowledge bank with decision trees &amp; best-practice libraries.</p></div>`).join("");

        $("#view").innerHTML = `
          <div class="page-head"><span class="eyebrow">Resources</span><h1>Templates, decision trees &amp; knowledge</h1>
            <p class="lede">${totalTemplates} templates and ${totalKnowledge} knowledge docs ship across the marketplace. Export the full documentation or jump into a plugin's knowledge bank.</p></div>

          <div class="grid cols-4" style="margin-bottom:8px">
            <a class="card" href="repo-guide.html" style="display:block"><div class="action-tile"><span class="ico">${svg("book")}</span><span><span class="t">Full Repo Guide</span><span class="d">Per-agent reference &amp; “I want to…” lookup</span></span></div></a>
            <a class="card" href="README.md" style="display:block"><div class="action-tile"><span class="ico">${svg("info")}</span><span><span class="t">README</span><span class="d">Marketplace overview &amp; setup</span></span></div></a>
            <a class="card" href="plugins/ravenclaude-core/dashboard.html" style="display:block"><div class="action-tile"><span class="ico">${svg("sliders")}</span><span><span class="t">Deep Dashboard</span><span class="d">Full posture &amp; tribunal controls</span></span></div></a>
            <a class="card" href="CHANGELOG.md" style="display:block"><div class="action-tile"><span class="ico">${svg("git")}</span><span><span class="t">Changelog</span><span class="d">Version history</span></span></div></a>
          </div>

          <div class="section-title"><h2>Templates gallery</h2><span class="hint">${totalTemplates} starter artifacts</span></div>
          <div class="grid cols-3">${templateCards}</div>

          <div class="section-title"><h2>Decision trees &amp; knowledge banks</h2><span class="hint">top knowledge banks</span></div>
          <div class="grid cols-3">${treeCards}</div>

          <div class="section-title"><h2>Best practices &amp; anti-patterns</h2></div>
          <div class="grid cols-2">
            <div class="card"><div style="display:flex;align-items:center;gap:8px"><span style="color:var(--allow)">${svg("check")}</span><b>House best practices</b></div><p style="color:var(--muted);font-size:.85rem;margin:8px 0 0">Method-before-library, effect-size + CI on every statistic, structured hand-offs, gates as the source of truth. Each plugin's advisory hook flags its own §3/§4 violations.</p></div>
            <div class="card"><div style="display:flex;align-items:center;gap:8px"><span style="color:var(--danger)">${svg("info")}</span><b>Anti-patterns flagged</b></div><p style="color:var(--muted);font-size:.85rem;margin:8px 0 0">SOQL/DML-in-loop, hardcoded rates, plaintext PII, per-viewer-priced BI for SMB, p-hacking, missing Sources/Assumptions — caught by per-plugin hooks at author time.</p></div>
          </div>

          <div class="section-title"><h2>Export documentation</h2></div>
          <div class="callout">${svg("download")}<span>Regenerate this dashboard and the full guide from source: <code>python3 scripts/generate-index-dashboard.py</code> and <code>python3 scripts/generate-repo-guide.py</code>. Both read the live catalog so the docs never drift.</span></div>`;
      }

      /* ---------------- Global search ---------------- */
      function buildSearchIndex() {
        const idx = [];
        D.plugins.forEach((p) => {
          idx.push({ kind: "plugin", label: p.label, meta: p.category_label, hay: (p.label + " " + p.description + " " + p.keywords.join(" ")).toLowerCase(), route: "#/marketplace/" + p.category, open: p.name });
          p.agents.forEach((a) => idx.push({ kind: "agent", label: a.label, meta: p.label, hay: (a.label + " " + a.description).toLowerCase(), route: "#/team" }));
        });
        return idx;
      }
      const SEARCH_IDX = buildSearchIndex();
      let searchCursor = -1, searchMatches = [];
      function runSearch(q) {
        const box = $("#search-results");
        q = q.toLowerCase().trim();
        if (!q) { box.classList.remove("open"); return; }
        searchMatches = SEARCH_IDX.filter((x) => x.hay.includes(q)).slice(0, 12);
        searchCursor = -1;
        box.innerHTML = searchMatches.length ? searchMatches.map((m, i) => `<div class="res" data-i="${i}" role="option"><span class="kind">${m.kind}</span><span>${esc(m.label)}</span><span class="meta">${esc(m.meta)}</span></div>`).join("") : `<div class="empty">No matches for “${esc(q)}”</div>`;
        box.classList.add("open");
        $$("#search-results .res").forEach((el) => el.addEventListener("click", () => gotoSearch(searchMatches[+el.dataset.i])));
      }
      function gotoSearch(m) {
        $("#search-results").classList.remove("open");
        $("#search-input").value = "";
        if (m.open) { location.hash = m.route; setTimeout(() => window.__openPlugin(m.open), 30); }
        else location.hash = m.route;
      }

      /* ---------------- Router ---------------- */
      function route() {
        const hash = location.hash.replace(/^#\/?/, "") || "home";
        const [section, sub] = hash.split("/");
        renderNav(NAV.some((n) => n.id === section) ? section : "home");
        document.body.classList.remove("mobile-nav-open");
        switch (section) {
          case "team": viewTeam(); break;
          case "marketplace": viewMarketplace(sub); break;
          case "configuration": viewConfiguration(); break;
          case "resources": viewResources(); break;
          case "home":
          default: viewHome(); break;
        }
        $("#view").focus({ preventScroll: true });
        window.scrollTo({ top: 0 });
      }
      window.addEventListener("hashchange", route);

      /* ---------------- Chrome wiring ---------------- */
      // Sidebar collapse (persisted)
      if (localStorage.getItem("rc-sidebar") === "collapsed") document.body.classList.add("sidebar-collapsed");
      $("#collapse-toggle").addEventListener("click", () => {
        document.body.classList.toggle("sidebar-collapsed");
        localStorage.setItem("rc-sidebar", document.body.classList.contains("sidebar-collapsed") ? "collapsed" : "open");
      });
      // Mobile nav
      $("#mobile-toggle").addEventListener("click", () => document.body.classList.toggle("mobile-nav-open"));
      $("#scrim").addEventListener("click", () => document.body.classList.remove("mobile-nav-open"));
      // Search
      const si = $("#search-input");
      si.addEventListener("input", (e) => runSearch(e.target.value));
      si.addEventListener("keydown", (e) => {
        const box = $("#search-results");
        if (e.key === "Escape") { si.value = ""; box.classList.remove("open"); si.blur(); }
        else if (e.key === "ArrowDown" || e.key === "ArrowUp") {
          e.preventDefault();
          searchCursor = Math.max(0, Math.min(searchMatches.length - 1, searchCursor + (e.key === "ArrowDown" ? 1 : -1)));
          $$("#search-results .res").forEach((el, i) => el.classList.toggle("cursor", i === searchCursor));
        } else if (e.key === "Enter" && searchMatches.length) {
          gotoSearch(searchMatches[Math.max(0, searchCursor)]);
        }
      });
      document.addEventListener("click", (e) => { if (!e.target.closest("#search")) $("#search-results").classList.remove("open"); });
      document.addEventListener("keydown", (e) => {
        if (e.key === "/" && document.activeElement !== si && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName)) { e.preventDefault(); si.focus(); }
      });

      route();
    </script>
  </body>
</html>
"""
