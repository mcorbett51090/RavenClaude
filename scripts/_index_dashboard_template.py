# Auto-loaded by generate-index-dashboard.py. Holds the self-contained
# HTML/CSS/JS shell for the redesigned RavenClaude landing dashboard.
#
# Placeholders substituted by the generator:
#   /*__RC_DATA__*/        → embedded JSON data object (window.__RC_DATA__)
#   /*__SHARED_TOKENS__*/  → :root contents from shared-tokens.css
#                            (read at generate-time, inlined as the design-system
#                            source of truth; see plugins/ravenclaude-core/
#                            dashboard-assets/README.md)
#   __GENERATED__          → human-readable generation timestamp
#   __MKT_VERSION__        → marketplace catalog version
#
# Keep this a RAW string (r"""...""") so the JS/CSS braces pass through verbatim.

TEMPLATE = r"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <title>RavenClaude — AI Engineering Team Platform</title>
    <meta name="description" content="RavenClaude is a private Claude Code plugin marketplace — a domain-neutral orchestration core plus specialist teams for Microsoft, Salesforce, web, data, finance and compliance. Browse plugins, the specialist roster, and the comfort-posture permission editor." />
    <meta name="color-scheme" content="light" />
    <meta name="theme-color" content="#faf7f0" />
    <meta name="robots" content="index, follow" />
    <link rel="canonical" href="index.html" />
    <!-- Open Graph / social -->
    <meta property="og:type" content="website" />
    <meta property="og:title" content="RavenClaude — AI Engineering Team Platform" />
    <meta property="og:description" content="A private Claude Code plugin marketplace: orchestration core + specialist teams, with a point-and-click comfort-posture permission editor." />
    <meta property="og:site_name" content="RavenClaude" />
    <meta name="twitter:card" content="summary" />
    <style>
      /* ── Shared tokens from plugins/ravenclaude-core/dashboard-assets/shared-tokens.css
         (substituted at generate-time by generate-index-dashboard.py). */
      /*__SHARED_TOKENS__*/

      /* ── Local aliases — map the existing index.html variables onto the
         shared tokens so the cascade lights this surface as light-beige +
         teal (the index/landing accent). Per-surface overrides live below. */
      :root {
        --bg: var(--rc-bg);
        --bg-2: var(--rc-surface-2);
        --surface: var(--rc-surface);
        --surface-2: var(--rc-surface-2);
        --surface-3: var(--rc-border);
        --border: var(--rc-border);
        --border-strong: var(--rc-border-strong);
        --text: var(--rc-text);
        --muted: var(--rc-muted);
        --faint: var(--rc-faint);
        --teal: var(--rc-teal);
        --teal-2: var(--rc-teal);
        --teal-dim: var(--rc-teal-soft);
        --teal-soft: rgba(31, 127, 120, 0.10);
        --teal-glow: rgba(31, 127, 120, 0.28);
        --ok: var(--rc-ok);
        --warn: var(--rc-warn);
        --danger: var(--rc-danger);
        --deny: var(--rc-danger);
        --ask: var(--rc-warn);
        --allow: var(--rc-ok);
        --font-sans: var(--rc-font-sans);
        --font-mono: var(--rc-font-mono);
        --radius: var(--rc-radius-lg);
        --radius-sm: var(--rc-radius-sm);
        --sidebar-w: 264px;
        --sidebar-collapsed: 72px;
        --topbar-h: 64px;
        --shadow: var(--rc-shadow-lg);
        --ring: var(--rc-focus-ring);
      }
      * { box-sizing: border-box; }
      html { scroll-behavior: smooth; }
      body {
        margin: 0;
        font-family: var(--font-sans);
        color: var(--text);
        background: var(--bg);
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
        min-height: 100vh;
      }
      a { color: var(--teal-2); text-decoration: none; }
      a:hover { color: var(--teal); }
      h1, h2, h3, h4 { letter-spacing: -0.02em; line-height: 1.15; margin: 0; }
      h1 { font-size: clamp(1.9rem, 4vw, 2.8rem); }
      p { line-height: 1.6; }
      ::selection { background: var(--teal); color: #fff; }
      :focus-visible { outline: none; box-shadow: var(--ring); border-radius: 8px; }
      button { font-family: inherit; cursor: pointer; }

      /* ---------- Layout shell ---------- */
      .app { display: grid; grid-template-columns: 64px var(--sidebar-w) 1fr; min-height: 100vh; transition: grid-template-columns 0.25s ease; }
      body.sidebar-collapsed .app { grid-template-columns: 64px var(--sidebar-collapsed) 1fr; }

      /* ---------- Icon rail (Intercom two-level nav: rail = sections) ---------- */
      .rail {
        position: sticky; top: 0; height: 100vh; width: 64px;
        background: var(--surface); border-right: 1px solid var(--border);
        display: flex; flex-direction: column; align-items: center; gap: 4px;
        padding: 12px 0; z-index: 41;
      }
      .rail-mark { width: 36px; height: 36px; flex: 0 0 auto; display: grid; place-items: center;
        border-radius: 10px; background: var(--teal-soft); border: 1px solid var(--border-strong); color: var(--teal-2); }
      .rail-mark svg { width: 20px; height: 20px; }
      .rail-nav { display: flex; flex-direction: column; align-items: center; gap: 6px; margin-top: 14px; width: 100%; }
      .rail-item { position: relative; width: 40px; height: 40px; display: grid; place-items: center;
        border-radius: 10px; color: var(--muted); transition: background 0.15s, color 0.15s; }
      .rail-item svg { width: 20px; height: 20px; }
      .rail-item:hover { background: var(--surface-2); color: var(--text); }
      .rail-item.active { background: var(--teal-soft); color: var(--teal-2); }
      .rail-item.active::before { content: ""; position: absolute; left: -12px; top: 9px; bottom: 9px; width: 3px; border-radius: 0 3px 3px 0; background: var(--teal); }

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
        background: rgba(255, 255, 255, 0.82); backdrop-filter: blur(12px);
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
      .btn.primary { background: var(--teal); color: #fff; border-color: var(--teal); box-shadow: var(--rc-shadow-sm); }
      .btn.primary:hover { background: var(--teal-dim); border-color: var(--teal-dim); }
      .btn.ghost { background: transparent; }
      .hide-sm { }

      /* ---------- Content ---------- */
      .content { padding: 28px clamp(16px, 4vw, 40px) 64px; max-width: 1320px; width: 100%; margin: 0 auto; animation: fade 0.35s ease; }
      @keyframes fade { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
      .page-head { margin-bottom: 24px; }
      .page-head .eyebrow { color: var(--teal-2); font-size: 0.74rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; }
      .page-head p.lede { color: var(--muted); margin-top: 8px; max-width: 70ch; }

      .card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; box-shadow: var(--rc-shadow-sm); transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.18s ease; }
      .card:hover { border-color: var(--border-strong); transform: translateY(-2px); box-shadow: var(--rc-shadow-md); }
      .grid { display: grid; gap: 16px; }
      .cols-2 { grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); }
      .cols-3 { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
      .cols-4 { grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); }

      /* Hero */
      .hero { position: relative; overflow: hidden; border-radius: var(--radius); padding: clamp(28px, 5vw, 52px); margin-bottom: 28px;
        background: var(--surface);
        border: 1px solid var(--border); box-shadow: var(--rc-shadow-sm); }
      /* Signature thin teal hairline across the hero top edge (minimal accent). */
      .hero::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, var(--teal) 50%, transparent); opacity: 0.55; }
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
      .yaml-panel pre { background: var(--surface-2); border: 1px solid var(--border); border-radius: 12px; padding: 14px; overflow: auto; max-height: 460px; font-family: var(--font-mono); font-size: 0.76rem; color: var(--text); line-height: 1.5; }
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
        .app { grid-template-columns: 64px 1fr !important; }
        .sidebar { position: fixed; left: 64px; top: 0; width: var(--sidebar-w); transform: translateX(-100%); transition: transform 0.25s ease; box-shadow: var(--shadow); }
        body.mobile-nav-open .sidebar { transform: translateX(0); }
        body.sidebar-collapsed .nav a.nav-item .label,
        body.sidebar-collapsed .brand .meta { display: revert; }
        .desktop-collapse { display: none; }
        .hide-sm { display: none; }
        .search kbd { display: none; }
      }
      @media (min-width: 821px) { .mobile-only { display: none; } }
      @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; scroll-behavior: auto; } }

      /* ──────────────────────────────────────────────────────────────────
         v0.103.0 — Intercom polish: ⌘K palette, dark mode wire, scenario
         picker upgrades, refined hover/focus states, micro-interactions.
         ────────────────────────────────────────────────────────────────── */

      /* Refined card hover — soft lift + warm shadow growth */
      .card { transition: transform 0.18s cubic-bezier(.4,0,.2,1), box-shadow 0.18s ease, border-color 0.18s ease; }
      .card:hover { transform: translateY(-1px); box-shadow: var(--rc-shadow-md, var(--shadow)); }

      /* Refined button states */
      .btn { transition: transform 0.12s ease, background 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease; }
      .btn:active { transform: scale(0.98); }
      .btn:focus-visible { box-shadow: var(--rc-focus-ring); outline: none; }

      /* Sidebar active-state rule animation */
      .nav a.nav-item.active::before { transition: width 0.18s ease, background 0.18s ease; }
      .nav a.nav-item.active:hover::before { width: 4px; }

      /* ── Theme toggle button (dark mode) ───────────────────────────── */
      .theme-toggle {
        width: 38px; height: 38px; display: grid; place-items: center;
        border-radius: 10px; background: var(--surface); border: 1px solid var(--border);
        color: var(--muted); cursor: pointer; transition: 0.15s;
      }
      .theme-toggle:hover { color: var(--text); border-color: var(--border-strong); background: var(--surface-2); }
      .theme-toggle:focus-visible { box-shadow: var(--rc-focus-ring); outline: none; }
      .theme-toggle svg { width: 18px; height: 18px; }
      .theme-toggle .moon { display: none; }
      [data-theme="dark"] .theme-toggle .sun { display: none; }
      [data-theme="dark"] .theme-toggle .moon { display: block; }

      /* ── ⌘K Command Palette ─────────────────────────────────────────── */
      .palette-backdrop {
        position: fixed; inset: 0; background: rgba(20, 17, 13, 0.55);
        backdrop-filter: blur(8px); z-index: 90; opacity: 0; pointer-events: none;
        transition: opacity 0.18s ease;
      }
      .palette-backdrop.open { opacity: 1; pointer-events: auto; }
      .palette {
        position: fixed; top: 15vh; left: 50%; transform: translateX(-50%) translateY(-12px);
        width: min(560px, calc(100vw - 32px));
        background: var(--surface); border: 1px solid var(--border-strong);
        border-radius: 14px; box-shadow: var(--rc-shadow-xl, var(--shadow));
        z-index: 91; opacity: 0; pointer-events: none;
        transition: opacity 0.18s ease, transform 0.18s cubic-bezier(.4,0,.2,1);
        display: flex; flex-direction: column; max-height: 70vh; overflow: hidden;
      }
      .palette.open { opacity: 1; transform: translateX(-50%) translateY(0); pointer-events: auto; }
      .palette-input-row { display: flex; align-items: center; gap: 10px; padding: 14px 16px; border-bottom: 1px solid var(--border); }
      .palette-input-row svg { width: 18px; height: 18px; color: var(--faint); flex: 0 0 auto; }
      .palette-input { flex: 1; background: transparent; border: none; outline: none; color: var(--text); font-family: inherit; font-size: 0.95rem; }
      .palette-input::placeholder { color: var(--faint); }
      .palette-input-row kbd { font-size: 0.68rem; color: var(--faint); border: 1px solid var(--border); border-radius: 6px; padding: 2px 6px; font-family: var(--font-mono); }
      .palette-results { overflow-y: auto; padding: 8px 0; }
      .palette-section { padding: 4px 8px; }
      .palette-section-label { font-size: 0.66rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--faint); padding: 8px 10px 6px; }
      .palette-item { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 9px; cursor: pointer; color: var(--text); }
      .palette-item:hover, .palette-item.cursor { background: var(--surface-2); }
      .palette-item .pi-ico { width: 18px; height: 18px; flex: 0 0 auto; color: var(--muted); }
      .palette-item .pi-label { font-size: 0.92rem; font-weight: 500; }
      .palette-item .pi-meta { margin-left: auto; font-size: 0.74rem; color: var(--faint); }
      .palette-item.cursor .pi-ico { color: var(--teal-2); }
      .palette-empty { padding: 24px 16px; text-align: center; color: var(--faint); font-size: 0.88rem; }
      .palette-empty .palette-hint { display: block; margin-top: 6px; font-size: 0.78rem; }
      .palette-foot { display: flex; align-items: center; gap: 12px; padding: 10px 16px; border-top: 1px solid var(--border); font-size: 0.72rem; color: var(--faint); flex: 0 0 auto; }
      .palette-foot kbd { font-size: 0.68rem; color: var(--muted); border: 1px solid var(--border); border-radius: 4px; padding: 1px 5px; font-family: var(--font-mono); }
      .palette-opener {
        flex: 1; max-width: 520px; height: 40px;
        display: flex; align-items: center; gap: 10px; padding: 0 12px;
        border-radius: 10px; background: var(--surface); border: 1px solid var(--border);
        color: var(--faint); cursor: pointer; transition: 0.15s;
        font-family: inherit; font-size: 0.88rem;
      }
      .palette-opener:hover { color: var(--text); border-color: var(--border-strong); background: var(--surface-2); }
      .palette-opener svg { width: 18px; height: 18px; flex: 0 0 auto; }
      .palette-opener .label { flex: 1; text-align: left; }
      .palette-opener kbd { font-size: 0.68rem; color: var(--faint); border: 1px solid var(--border); border-radius: 6px; padding: 2px 6px; font-family: var(--font-mono); }

      /* ── Scenario picker (Configuration view) ──────────────────────── */
      .scenario-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 14px; margin-bottom: 24px; }
      .scenario-card {
        position: relative; padding: 18px;
        background: var(--surface); border: 1px solid var(--border);
        border-radius: 14px; cursor: pointer;
        transition: transform 0.18s cubic-bezier(.4,0,.2,1), box-shadow 0.18s ease, border-color 0.18s ease;
        text-align: left;
      }
      .scenario-card:hover { transform: translateY(-2px); box-shadow: var(--rc-shadow-md, var(--shadow)); border-color: var(--border-strong); }
      .scenario-card.active { box-shadow: var(--rc-shadow-md, var(--shadow)); }
      .scenario-card[data-profile="strict"].active { border-color: var(--rc-gold, #b8923a); }
      .scenario-card[data-profile="balanced"].active { border-color: var(--rc-teal, var(--teal)); }
      .scenario-card[data-profile="exploratory"].active { border-color: var(--rc-border-strong, var(--border-strong)); }
      .scenario-card[data-profile="autonomous"].active { border-color: #b5630a; }
      .scenario-card .sc-tag {
        position: absolute; top: 12px; right: 12px;
        font-size: 0.66rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
        color: var(--teal-2); padding: 3px 8px; background: var(--teal-soft);
        border: 1px solid var(--border-strong); border-radius: 999px;
      }
      .scenario-card .sc-name { font-weight: 700; font-size: 1.05rem; margin-bottom: 6px; letter-spacing: -0.01em; }
      .scenario-card .sc-blurb { color: var(--muted); font-size: 0.84rem; line-height: 1.5; margin-bottom: 14px; }
      .scenario-card .sc-means { display: flex; flex-direction: column; gap: 6px; font-size: 0.78rem; color: var(--muted); }
      .scenario-card .sc-means .sm-line { display: flex; gap: 8px; align-items: baseline; }
      .scenario-card .sc-means .sm-bullet { color: var(--faint); }

      .pcat-row { display: flex; flex-direction: column; padding: 14px 0; border-bottom: 1px solid var(--border); }
      .pcat-row-head { display: flex; align-items: center; gap: 14px; }
      .pcat-row-head .pc-info { flex: 1; min-width: 0; }
      .pcat-row-head .pc-info .t { font-weight: 600; font-size: 0.92rem; }
      .pcat-row-head .pc-info .d { color: var(--muted); font-size: 0.8rem; margin-top: 2px; }
      .pcat-row-head .pc-drift { width: 8px; height: 8px; border-radius: 50%; background: var(--rc-gold, #b8923a); }
      .pcat-why-btn { background: transparent; border: none; color: var(--faint); font-size: 0.78rem; cursor: pointer; padding: 6px 0 0 0; align-self: flex-start; }
      .pcat-why-btn:hover { color: var(--text); }
      .pcat-why { display: none; margin-top: 10px; padding: 10px 12px; background: var(--surface-2); border-radius: 8px; font-size: 0.82rem; color: var(--muted); line-height: 1.55; }
      .pcat-why.open { display: block; }
      .pcat-why .pw-label { font-weight: 600; color: var(--text); margin-bottom: 4px; font-size: 0.78rem; }
      .pcat-why ul { margin: 6px 0 0; padding-left: 18px; }
      .pcat-why code { font-family: var(--font-mono); font-size: 0.78rem; }

      /* YAML preview syntax color */
      .yaml-panel pre .yk { color: var(--teal-2); }
      .yaml-panel pre .yv { color: var(--text); }
      .yaml-panel pre .yc { color: var(--faint); font-style: italic; }

      /* ── Onboarding checklist ──────────────────────────────────────── */
      .onboarding-card {
        background: var(--surface);
        border: 1px solid var(--border); border-radius: var(--radius); box-shadow: var(--rc-shadow-sm);
        padding: 20px 22px; margin-bottom: 22px;
      }
      .onboarding-head { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }
      .onboarding-head h2 { font-size: 1.1rem; letter-spacing: -0.01em; }
      .onboarding-head .ob-progress { margin-left: auto; font-size: 0.72rem; color: var(--muted); background: var(--surface); border: 1px solid var(--border); border-radius: 999px; padding: 4px 10px; font-family: var(--font-mono); }
      .onboarding-head .ob-dismiss { background: transparent; border: none; color: var(--faint); cursor: pointer; padding: 4px 8px; border-radius: 6px; }
      .onboarding-head .ob-dismiss:hover { color: var(--text); background: var(--surface); }
      .onboarding-steps { display: flex; flex-direction: column; gap: 6px; }
      .onboarding-step { display: flex; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 9px; cursor: pointer; transition: background 0.15s ease; }
      .onboarding-step:hover { background: var(--surface); }
      .onboarding-step .step-check { width: 22px; height: 22px; flex: 0 0 auto; border-radius: 50%; border: 1.5px solid var(--border-strong); display: grid; place-items: center; color: transparent; transition: 0.15s; }
      .onboarding-step.done .step-check { background: var(--teal-2); border-color: var(--teal-2); color: var(--surface); }
      .onboarding-step.done .step-check svg { width: 12px; height: 12px; }
      .onboarding-step .step-body { flex: 1; }
      .onboarding-step .step-title { font-size: 0.92rem; font-weight: 500; color: var(--text); }
      .onboarding-step.done .step-title { text-decoration: line-through; color: var(--muted); }
      .onboarding-step .step-action { font-size: 0.74rem; color: var(--faint); }
      .onboarding-step .step-cta { margin-left: auto; padding: 6px 10px; border-radius: 6px; font-size: 0.78rem; background: transparent; border: 1px solid var(--border); color: var(--muted); cursor: pointer; }
      .onboarding-step .step-cta:hover { color: var(--text); border-color: var(--border-strong); background: var(--surface); }

      /* Spawn feedback widget */
      .spawn-card { padding: 16px 18px; }
      .spawn-card .sp-head { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; font-size: 0.78rem; color: var(--faint); text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700; }
      .spawn-card .sp-team { font-weight: 600; font-size: 0.92rem; }
      .spawn-card .sp-roster { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }

      /* Toast action button */
      .toast .toast-msg { flex: 1; }
      .toast .toast-action { background: transparent; border: 1px solid var(--teal); color: var(--teal-2); padding: 4px 10px; border-radius: 6px; font-size: 0.78rem; cursor: pointer; margin-left: 12px; }
      .toast .toast-action:hover { background: var(--teal-soft); }
      .toast { display: flex; align-items: center; min-width: 280px; }

      /* Empty-state illustration */
      .empty-illustration { width: 64px; height: 64px; margin: 0 auto 14px; color: var(--faint); opacity: 0.5; }

      /* Hero shine — once on first paint, not looping */
      .hero h1 .accent { background-size: 200% 100%; animation: rcShimmerOnce 1.6s cubic-bezier(.4,0,.2,1) 0.3s 1 backwards; }

      /* Stagger entry — first 5 cards, then uniform 250ms tail */
      .content > *:nth-child(1) { animation: rcFadeUp 0.4s ease backwards; animation-delay: 0ms; }
      .content > *:nth-child(2) { animation: rcFadeUp 0.4s ease backwards; animation-delay: 50ms; }
      .content > *:nth-child(3) { animation: rcFadeUp 0.4s ease backwards; animation-delay: 100ms; }
      .content > *:nth-child(4) { animation: rcFadeUp 0.4s ease backwards; animation-delay: 150ms; }
      .content > *:nth-child(5) { animation: rcFadeUp 0.4s ease backwards; animation-delay: 200ms; }
      .content > *:nth-child(n+6) { animation: rcFadeUp 0.4s ease backwards; animation-delay: 250ms; }
    </style>
  </head>
  <body>
    <div class="scrim" id="scrim" aria-hidden="true"></div>
    <div class="app">
      <!-- ======================= ICON RAIL ======================= -->
      <aside class="rail" aria-label="Sections">
        <a class="rail-mark" href="#/home" aria-label="RavenClaude home">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M3 11l9-7 9 7v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><path d="M9 21v-7h6v7" stroke="currentColor"/></svg>
        </a>
        <nav class="rail-nav" id="rail-nav" aria-label="Primary sections"></nav>
      </aside>
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
          <button class="palette-opener" id="palette-opener" aria-label="Open command palette (Cmd+K)">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
            <span class="label">Search plugins, agents, actions…</span>
            <kbd>⌘K</kbd>
          </button>
          <div class="actions">
            <button class="theme-toggle" id="theme-toggle" aria-label="Toggle dark mode" type="button">
              <svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/></svg>
              <svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z"/></svg>
            </button>
            <a class="btn ghost hide-sm" href="repo-guide.html"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>Repo Guide</a>
            <a class="btn primary" href="#/marketplace"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v4H3z"/><path d="M5 7v12h14V7"/><path d="M9 11h6"/></svg>Browse Plugins</a>
          </div>
        </header>
        <main class="content" id="view" tabindex="-1"></main>
      </div>
    </div>

    <!-- ⌘K Command Palette -->
    <div class="palette-backdrop" id="palette-backdrop" aria-hidden="true"></div>
    <div class="palette" id="palette" role="dialog" aria-modal="true" aria-labelledby="palette-input" tabindex="-1">
      <div class="palette-input-row">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
        <input class="palette-input" id="palette-input" type="text" placeholder="Search plugins, agents, actions…" autocomplete="off" aria-label="Command palette search" />
        <kbd>esc</kbd>
      </div>
      <div class="palette-results" id="palette-results" role="listbox"></div>
      <div class="palette-foot">
        <span><kbd>↑</kbd><kbd>↓</kbd> navigate</span>
        <span><kbd>↵</kbd> select</span>
        <span><kbd>esc</kbd> close</span>
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
        const rail = $("#rail-nav");
        if (rail) {
          rail.innerHTML = NAV.map((n) => `<a class="rail-item${n.id === active ? " active" : ""}" href="#/${n.id}" title="${n.label}" aria-label="${n.label}"${n.id === active ? ' aria-current="page"' : ""}>${svg(n.icon)}</a>`).join("");
        }
      }

      /* ---------------- Toast ----------------
         Backward-compatible overload: existing callers pass a string and
         get the same banner. New callers can pass {msg, action:{label,fn}}
         to attach a follow-up action button; dismiss timer extends to 5s
         when an action is present (WCAG 2.2.1 timing). */
      let toastT;
      function toast(msgOrObj) {
        const t = $("#toast");
        const opts = (typeof msgOrObj === "string") ? { msg: msgOrObj } : (msgOrObj || {});
        const dismissMs = opts.action ? 5000 : 2400;
        t.innerHTML = `<span class="toast-msg"></span>`;
        t.querySelector(".toast-msg").textContent = opts.msg || "";
        if (opts.action && typeof opts.action.fn === "function") {
          const btn = document.createElement("button");
          btn.className = "toast-action";
          btn.textContent = opts.action.label || "Action";
          btn.addEventListener("click", () => { opts.action.fn(); t.classList.remove("show"); });
          t.appendChild(btn);
        }
        t.classList.add("show");
        clearTimeout(toastT);
        toastT = setTimeout(() => t.classList.remove("show"), dismissMs);
      }
      function copyText(text, label) {
        navigator.clipboard?.writeText(text).then(
          () => toast((label || "Copied") + " to clipboard"),
          () => toast("Copy failed — select & copy manually")
        );
      }
      window.__copy = copyText;

      /* ---------------- Onboarding ----------------
         Dismissible 5-step checklist on Home. State in localStorage
         (rc-onboarding-progress = bit-flag int, rc-onboarding-dismissed
         = "1"). Re-show via ⌘K → "Show onboarding checklist". */
      const ONBOARDING_STEPS = [
        { id: 0, title: "Install ravenclaude-core", desc: "Copy the install command", cta: "Copy", action: "copyCmd", cmd: "/plugin install ravenclaude-core@ravenclaude" },
        { id: 1, title: "Pick a posture scenario", desc: "Recommended: Client Delivery", cta: "Open", action: "route", route: "#/configuration" },
        { id: 2, title: "Read GETTING_STARTED.md", desc: "10-minute canonical walkthrough", cta: "Open", action: "href", href: "GETTING_STARTED.md" },
        { id: 3, title: "Run your first /spawn-team", desc: "Copy an example prompt", cta: "Copy", action: "copyCmd", cmd: "/spawn-team architect → coder → tester for: <describe your change>" },
        { id: 4, title: "Open the deep posture dashboard", desc: "Save & apply writes .ravenclaude/comfort-posture.yaml", cta: "Copy", action: "copyCmd", cmd: "bash scripts/open-dashboard.sh" },
      ];
      function onboardingProgress() {
        return parseInt(localStorage.getItem("rc-onboarding-progress") || "0", 10);
      }
      function onboardingMark(id) {
        const cur = onboardingProgress();
        const next = cur | (1 << id);
        localStorage.setItem("rc-onboarding-progress", String(next));
      }
      function onboardingDone(id) { return (onboardingProgress() & (1 << id)) !== 0; }
      function onboardingDismissed() { return localStorage.getItem("rc-onboarding-dismissed") === "1"; }
      function onboardingComplete() {
        return ONBOARDING_STEPS.every((s) => onboardingDone(s.id));
      }
      function onboardingHtml() {
        if (onboardingDismissed() || onboardingComplete()) return "";
        const doneCount = ONBOARDING_STEPS.filter((s) => onboardingDone(s.id)).length;
        const stepsHtml = ONBOARDING_STEPS.map((s) => {
          const done = onboardingDone(s.id);
          const checkSvg = done ? svg("check") : "";
          return `<div class="onboarding-step${done ? " done" : ""}" data-step="${s.id}" data-action="${esc(s.action)}" data-cmd="${esc(s.cmd || "")}" data-href="${esc(s.href || "")}" data-route="${esc(s.route || "")}">
            <span class="step-check">${checkSvg}</span>
            <div class="step-body"><div class="step-title">${esc(s.title)}</div><div class="step-action">${esc(s.desc)}</div></div>
            <button class="step-cta" type="button">${esc(s.cta)}</button>
          </div>`;
        }).join("");
        return `<div class="onboarding-card" id="onboarding-card">
          <div class="onboarding-head">
            ${svg("rocket")}
            <h2>Welcome — get started in 10 minutes</h2>
            <span class="ob-progress">${doneCount} of ${ONBOARDING_STEPS.length}</span>
            <button class="ob-dismiss" id="ob-dismiss" type="button" aria-label="Dismiss onboarding">×</button>
          </div>
          <div class="onboarding-steps">${stepsHtml}</div>
        </div>`;
      }
      function spawnLogHtml() {
        let entry = null;
        try { entry = JSON.parse(localStorage.getItem("rc-spawn-log") || "null"); } catch (e) { entry = null; }
        if (!entry || !entry.playbook) return "";
        const roster = (entry.agents || []).map((a) => `<span class="chip teal">${esc(a)}</span>`).join("");
        return `<div class="card spawn-card">
          <div class="sp-head">${svg("team")}<span>Last team spawned</span></div>
          <div class="sp-team">${esc(entry.playbook)} playbook</div>
          <div class="sp-roster">${roster}</div>
        </div>`;
      }

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
          ${onboardingHtml()}
          ${spawnLogHtml()}
          <section class="hero">
            <span class="pill">${svg("spark")} Private Claude Code marketplace · v${esc(D.marketplace_version)}</span>
            <h1>The <span class="accent">AI Engineering Team</span> Platform</h1>
            <p>One main helper that runs the show, plus ${s.plugins - 1} expert teams — for Microsoft, Salesforce, web, data, finance, and safety-and-rules work. They plug into Claude Code, and <strong>you</strong> decide what they can do on their own using simple point-and-click settings.</p>
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
        // Wire onboarding step buttons
        const ob = $("#onboarding-card");
        if (ob) {
          $("#ob-dismiss").addEventListener("click", () => { localStorage.setItem("rc-onboarding-dismissed", "1"); ob.remove(); toast({ msg: "Onboarding hidden. Reopen via ⌘K → Show onboarding checklist" }); });
          $$(".onboarding-step").forEach((step) => {
            const id = parseInt(step.dataset.step, 10);
            const act = step.dataset.action;
            const cmd = step.dataset.cmd;
            const href = step.dataset.href;
            const rt = step.dataset.route;
            const trigger = () => {
              if (act === "copyCmd" && cmd) window.__copy(cmd, "Command");
              else if (act === "href" && href) window.open(href, "_blank", "noopener");
              else if (act === "route" && rt) location.hash = rt;
              onboardingMark(id);
              step.classList.add("done");
              const check = step.querySelector(".step-check");
              if (check && !check.innerHTML.trim()) check.innerHTML = svg("check");
              // Update progress count
              const pg = $(".onboarding-card .ob-progress");
              if (pg) pg.textContent = `${ONBOARDING_STEPS.filter((s) => onboardingDone(s.id)).length} of ${ONBOARDING_STEPS.length}`;
              // Auto-hide when complete
              if (onboardingComplete()) {
                setTimeout(() => { ob.remove(); toast({ msg: "Onboarding complete — nice work!" }); }, 800);
              }
            };
            step.querySelector(".step-cta").addEventListener("click", (e) => { e.stopPropagation(); trigger(); });
          });
        }
      }

      /* ---------------- TEAM ---------------- */
      const allAgents = () => D.plugins.flatMap((p) => p.agents.map((a) => ({ ...a, plugin: p.name, pluginLabel: p.label, domain: p.category_label })));
      function viewTeam() {
        const agents = allAgents();
        const domains = [...new Set(agents.map((a) => a.domain))].sort();
        $("#view").innerHTML = `
          <div class="page-head"><span class="eyebrow">The Team</span><h1>Specialist roster &amp; collaboration</h1>
            <p class="lede">${agents.length} agents across ${D.plugins.length} plugins. One agent — the Team Lead — hands out the work, and the expert agents do it. Search the list below, look through the skills they can use and the safety checks that run, and read the rules for how they pass work to each other.</p></div>

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
            <p class="lede">${D.plugins.length} ready-made plugins, sorted by topic. Each one comes with expert agents, skills they can use, and a built-in pile of know-how. Pick a group, or search across all of them.</p></div>
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
        // ⌘K palette can pre-stage a preset; apply if pending
        if (window.__pendingPreset) {
          const pid = window.__pendingPreset;
          window.__pendingPreset = null;
          if (D.posture.presets.some((p) => p.id === pid)) {
            applyPreset(pid);
            setTimeout(() => toast({ msg: `Applied "${(D.posture.presets.find((p) => p.id === pid) || {}).label || pid}"`, action: { label: "Save YAML", fn: () => copyText(postureYaml(), "comfort-posture.yaml") } }), 100);
          }
        }
        const groups = {};
        D.posture.categories.forEach((c) => { (groups[c.group] = groups[c.group] || []).push(c); });
        // Scenario picker — visual cards with auto-generated "what this means" prose
        const PROFILE_MAP = { strict_production: "strict", client_delivery: "balanced", exploratory: "exploratory", maximum_autonomy: "autonomous" };
        const LEVEL_PHRASE = { deny: "always stops you", ask: "asks before acting", allow: "proceeds silently" };
        function meansFor(preset) {
          // Pick 3 highest-stakes categories (deny > ask > auto) and render via template
          const ranks = { deny: 3, ask: 2, allow: 1 };
          const entries = D.posture.categories
            .map((c) => ({ c, lv: (preset.levels && preset.levels[c.id]) || preset.global_default || "ask" }))
            .sort((a, b) => (ranks[b.lv] || 0) - (ranks[a.lv] || 0));
          return entries.slice(0, 3).map((e) => `${e.c.title}: ${LEVEL_PHRASE[e.lv] || e.lv}`);
        }
        const scenarioGrid = D.posture.presets.map((p) => {
          const profile = PROFILE_MAP[p.id] || "balanced";
          const tag = p.id === "client_delivery" ? `<span class="sc-tag">Recommended</span>` : "";
          const means = meansFor(p);
          const lines = means.map((m) => `<div class="sm-line"><span class="sm-bullet">•</span><span>${esc(m)}</span></div>`).join("");
          return `<button type="button" class="scenario-card${p.id === posture.activePreset ? " active" : ""}" data-preset="${esc(p.id)}" data-profile="${profile}" aria-pressed="${p.id === posture.activePreset}">
            ${tag}
            <div class="sc-name">${esc(p.label)}</div>
            <div class="sc-blurb">${esc(p.blurb)}</div>
            <div class="sc-means">${lines}</div>
          </button>`;
        }).join("");
        const presetRow = D.posture.presets.map((p) => `<button class="preset-btn${p.id === posture.activePreset ? " active" : ""}" data-preset="${p.id}"><span>${esc(p.label)}</span><small>${esc(p.blurb)}</small></button>`).join("");
        const groupHtml = Object.entries(groups).map(([g, cats]) => `
          <div class="pcat-group"><h4>${esc(g)}</h4>${cats.map((c) => `
            <div class="pcat" data-cat="${c.id}">
              <div class="pc-info"><div class="t">${esc(c.title)}</div><div class="d">${esc(c.description)}${c.recommended ? ` · <span style="color:var(--teal-2)">recommended: ${esc(c.recommended)}</span>` : ""}</div></div>
              <div class="seg" role="group" aria-label="${esc(c.title)} level">${D.posture.levels.map((lv) => `<button type="button" data-level="${lv}" data-cat="${c.id}">${lv}</button>`).join("")}</div>
            </div>`).join("")}</div>`).join("");

        $("#view").innerHTML = `
          <div class="page-head"><span class="eyebrow">Configuration</span><h1>Comfort posture &amp; environment</h1>
            <p class="lede">Decide how much your agents can do without stopping to ask you. For each kind of action, pick one of three levels: <b>deny</b> (never), <b>ask</b> (check with me first), or <b>allow</b> (go ahead). Start from a ready-made profile, change what you want, then copy the <code>comfort-posture.yaml</code> file it makes. A few always-on safety rules can never be turned off.</p></div>

          <div class="callout" style="margin-bottom:20px">${svg("info")}<span>This editor produces the <b>project-layer</b> baseline. For the full per-layer (user / local / project) editor with live writes to <code>.claude/settings.json</code>, open the deep dashboard via <code>/dashboard</code> or <a href="plugins/ravenclaude-core/dashboard.html">dashboard.html</a>.</span></div>

          <div class="section-title"><h2>Pick a scenario</h2><span class="hint">visual presets — fine-tune below if needed</span></div>
          <div class="scenario-grid" id="scenario-grid">${scenarioGrid}</div>

          <div class="section-title"><h2>Or browse all presets</h2><span class="hint">same content, compact form</span></div>
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
        $("#preset-row").addEventListener("click", (e) => { const b = e.target.closest(".preset-btn"); if (!b) return; applyPreset(b.dataset.preset); refresh(); toast({ msg: `Applied "${b.querySelector("span").textContent}" profile`, action: { label: "Copy YAML", fn: () => copyText(postureYaml(), "comfort-posture.yaml") } }); });
        $("#scenario-grid").addEventListener("click", (e) => { const b = e.target.closest(".scenario-card"); if (!b) return; const pid = b.dataset.preset; const preset = D.posture.presets.find((p) => p.id === pid); applyPreset(pid); refresh(); $$(".scenario-card").forEach((c) => c.classList.toggle("active", c.dataset.preset === pid)); toast({ msg: `Applied "${preset.label}"`, action: { label: "Copy YAML", fn: () => copyText(postureYaml(), "comfort-posture.yaml") } }); });
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

      /* ---------------- ⌘K Command Palette ----------------
         Categorized search across plugins, specialists, skills, hooks,
         and a set of "Quick action" commands. Built once at init from D.
         Keyboard nav: arrows + enter, esc closes, tab cycles within modal. */
      function buildPaletteIndex() {
        const idx = [];
        // Quick actions — top-priority category, always present
        const QA = [
          { kind: "action", label: "Apply Strict Production posture", meta: "Configuration", hay: "apply strict production posture", route: "#/configuration", preset: "strict_production" },
          { kind: "action", label: "Apply Client Delivery posture (recommended)", meta: "Configuration", hay: "apply client delivery posture recommended", route: "#/configuration", preset: "client_delivery" },
          { kind: "action", label: "Apply Exploratory posture", meta: "Configuration", hay: "apply exploratory posture", route: "#/configuration", preset: "exploratory" },
          { kind: "action", label: "Apply Maximum Autonomy posture", meta: "Configuration", hay: "apply maximum autonomy posture", route: "#/configuration", preset: "maximum_autonomy" },
          { kind: "action", label: "Open posture editor", meta: "Configuration", hay: "open posture editor configuration", route: "#/configuration" },
          { kind: "action", label: "Open deep dashboard", meta: "External", hay: "open deep dashboard server", action: "copyCmd", cmd: "bash scripts/open-dashboard.sh" },
          { kind: "action", label: "Toggle dark mode", meta: "Theme", hay: "toggle dark mode theme", action: "toggleTheme" },
          { kind: "action", label: "Show onboarding checklist", meta: "Onboarding", hay: "show onboarding checklist setup", action: "showOnboarding" },
          { kind: "action", label: "Open repo guide", meta: "External", hay: "open repo guide reference", href: "repo-guide.html" },
        ];
        QA.forEach((q) => idx.push(q));
        // Plugins
        D.plugins.forEach((p) => {
          idx.push({ kind: "plugin", label: p.label, meta: p.category_label, hay: (p.label + " " + p.description + " " + p.keywords.join(" ")).toLowerCase(), route: "#/marketplace/" + p.category, open: p.name });
          // Copy-install action per plugin
          idx.push({ kind: "action", label: `Copy install command for ${p.label}`, meta: "Install", hay: `copy install ${p.name} ${p.label}`.toLowerCase(), action: "copyCmd", cmd: `/plugin install ${p.name}@ravenclaude` });
        });
        // Specialists
        D.plugins.forEach((p) => p.agents.forEach((a) => idx.push({ kind: "specialist", label: a.label, meta: p.label, hay: (a.label + " " + (a.description || "") + " " + p.label).toLowerCase(), route: "#/team" })));
        // Skills (new — from §G scanner)
        D.plugins.forEach((p) => (p.skills_index || []).forEach((s) => idx.push({ kind: "skill", label: s.label, meta: p.label, hay: (s.label + " " + (s.description || "") + " " + p.label).toLowerCase(), route: "#/marketplace/" + p.category, open: p.name })));
        // Hooks (new — from §G scanner)
        D.plugins.forEach((p) => (p.hooks_index || []).forEach((h) => idx.push({ kind: "hook", label: h.name, meta: p.label + " · " + h.event, hay: (h.name + " " + (h.description || "") + " " + p.label).toLowerCase(), route: "#/marketplace/" + p.category, open: p.name })));
        return idx;
      }
      const PALETTE_IDX = buildPaletteIndex();
      const PALETTE_SECTIONS = [
        { key: "action", label: "Quick actions" },
        { key: "plugin", label: "Plugins" },
        { key: "specialist", label: "Specialists" },
        { key: "skill", label: "Skills" },
        { key: "hook", label: "Hooks" },
      ];
      const PALETTE_ICONS = { action: "rocket", plugin: "market", specialist: "team", skill: "spark", hook: "shield" };
      let paletteCursor = -1, paletteFlat = [];

      function renderPalette(q) {
        const box = $("#palette-results");
        q = (q || "").toLowerCase().trim();
        const matches = q ? PALETTE_IDX.filter((x) => x.hay.includes(q)) : PALETTE_IDX.filter((x) => x.kind === "action").slice(0, 6);
        paletteFlat = [];
        paletteCursor = -1;
        if (!matches.length) {
          box.innerHTML = `<div class="palette-empty">No matches.<span class="palette-hint">Try <code>/dashboard</code>, <code>power-platform</code>, or <code>strict posture</code>.</span></div>`;
          return;
        }
        let html = "";
        PALETTE_SECTIONS.forEach((sec) => {
          const inSec = matches.filter((m) => m.kind === sec.key).slice(0, 5);
          if (!inSec.length) return;
          html += `<div class="palette-section"><div class="palette-section-label">${sec.label}</div>`;
          inSec.forEach((m) => {
            const i = paletteFlat.length;
            paletteFlat.push(m);
            const ico = svg(PALETTE_ICONS[sec.key] || "sparkle");
            html += `<div class="palette-item" data-i="${i}" role="option"><span class="pi-ico">${ico}</span><span class="pi-label">${esc(m.label)}</span><span class="pi-meta">${esc(m.meta || "")}</span></div>`;
          });
          html += `</div>`;
        });
        box.innerHTML = html;
        $$("#palette-results .palette-item").forEach((el) => {
          el.addEventListener("click", () => paletteAction(paletteFlat[+el.dataset.i]));
          el.addEventListener("mouseenter", () => { paletteCursor = +el.dataset.i; updatePaletteCursor(); });
        });
      }
      function updatePaletteCursor() {
        $$("#palette-results .palette-item").forEach((el, i) => el.classList.toggle("cursor", i === paletteCursor));
        const cur = $$("#palette-results .palette-item")[paletteCursor];
        if (cur) cur.scrollIntoView({ block: "nearest" });
      }
      function paletteAction(m) {
        if (!m) return;
        closePalette();
        if (m.preset) {
          // Apply preset action — navigate to configuration; the view applies the preset on render
          window.__pendingPreset = m.preset;
          location.hash = m.route;
        } else if (m.action === "copyCmd" && m.cmd) {
          window.__copy(m.cmd, `Command ${m.cmd}`);
        } else if (m.action === "toggleTheme") {
          toggleTheme();
        } else if (m.action === "showOnboarding") {
          localStorage.removeItem("rc-onboarding-dismissed");
          if (location.hash !== "#/home" && location.hash !== "") location.hash = "#/home";
          else route();
        } else if (m.href) {
          window.location.href = m.href;
        } else if (m.open) {
          location.hash = m.route;
          setTimeout(() => window.__openPlugin(m.open), 30);
        } else {
          location.hash = m.route;
        }
      }
      function openPalette() {
        $("#palette").classList.add("open");
        $("#palette-backdrop").classList.add("open");
        const inp = $("#palette-input");
        inp.value = "";
        renderPalette("");
        setTimeout(() => inp.focus(), 30);
      }
      function closePalette() {
        $("#palette").classList.remove("open");
        $("#palette-backdrop").classList.remove("open");
        $("#palette-opener").focus();
      }
      // Backward compatibility: existing code (gotoSearch) may be referenced elsewhere
      const SEARCH_IDX = PALETTE_IDX;
      function gotoSearch(m) { paletteAction(m); }

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

      // ⌘K Palette wiring
      $("#palette-opener").addEventListener("click", openPalette);
      $("#palette-backdrop").addEventListener("click", closePalette);
      $("#palette-input").addEventListener("input", (e) => renderPalette(e.target.value));
      $("#palette-input").addEventListener("keydown", (e) => {
        if (e.key === "Escape") { closePalette(); }
        else if (e.key === "ArrowDown" || e.key === "ArrowUp") {
          e.preventDefault();
          paletteCursor = Math.max(0, Math.min(paletteFlat.length - 1, paletteCursor + (e.key === "ArrowDown" ? 1 : -1)));
          updatePaletteCursor();
        } else if (e.key === "Enter" && paletteFlat.length) {
          paletteAction(paletteFlat[Math.max(0, paletteCursor)]);
        }
      });

      // Theme toggle controller (auto-detect + manual override, persisted)
      function applyTheme(theme) {
        if (theme === "system") document.documentElement.removeAttribute("data-theme");
        else document.documentElement.setAttribute("data-theme", theme);
      }
      function currentTheme() {
        const saved = localStorage.getItem("rc-theme");
        if (saved === "dark" || saved === "light") return saved;
        return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      }
      function toggleTheme() {
        const next = currentTheme() === "dark" ? "light" : "dark";
        localStorage.setItem("rc-theme", next);
        applyTheme(next);
        toast({ msg: `Theme: ${next}` });
      }
      // Initial theme application
      applyTheme(localStorage.getItem("rc-theme") || (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"));
      $("#theme-toggle").addEventListener("click", toggleTheme);

      // Global key bindings: ⌘K / Ctrl+K opens palette; / opens palette too (when not typing)
      document.addEventListener("keydown", (e) => {
        const inField = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openPalette(); }
        else if (e.key === "/" && !inField) { e.preventDefault(); openPalette(); }
      });

      route();
    </script>
  </body>
</html>
"""
