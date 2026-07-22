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
    <meta name="theme-color" content="#07080a" />
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
         shared tokens so the cascade lights this surface as cool near-black +
         teal (the index/landing secondary accent; the dashboard carries the
         commerce green). Per-surface overrides live below. */
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
        --font-display: var(--rc-font-display);
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
      h1, h2, h3, h4 { font-family: var(--font-display); letter-spacing: -0.02em; line-height: 1.15; margin: 0; }
      h1 { font-size: clamp(1.9rem, 4vw, 2.8rem); }
      p { line-height: 1.6; }
      ::selection { background: var(--teal); color: #fff; }
      :focus-visible { outline: none; box-shadow: var(--ring); border-radius: 8px; }
      button { font-family: inherit; cursor: pointer; }

      /* ---------- Layout shell ---------- */
      .app { display: grid; grid-template-columns: var(--sidebar-w) 1fr; min-height: 100vh; transition: grid-template-columns 0.25s ease; }
      body.sidebar-collapsed .app { grid-template-columns: var(--sidebar-collapsed) 1fr; }

      /* Sidebar nav subcategories — model-driven accordion under the active item */
      .nav-sub { display: flex; flex-direction: column; gap: 2px; margin: 2px 0 6px; }
      .nav-subitem { display: flex; align-items: center; gap: 8px; padding: 7px 12px 7px 42px; border-radius: var(--radius-sm);
        color: var(--muted); font-size: 0.84rem; white-space: nowrap; transition: background 0.15s, color 0.15s; }
      .nav-subitem:hover { background: var(--surface); color: var(--text); }
      .nav-subitem.active { color: var(--teal-2); font-weight: 600; }
      .nav-subitem .count { margin-left: auto; font-size: 0.72rem; color: var(--faint); }
      body.sidebar-collapsed .nav-sub { display: none; }

      /* ---------- Sidebar ---------- */
      .sidebar {
        position: sticky; top: 0; height: 100vh;
        background: linear-gradient(180deg, var(--bg-2), var(--bg));
        border-right: 1px solid var(--border);
        display: flex; flex-direction: column;
        overflow: hidden; z-index: 40;
      }
      .brand { display: flex; align-items: center; gap: 12px; padding: 16px 18px; height: var(--topbar-h); border-bottom: 1px solid var(--border); white-space: nowrap; }
      .brand .mark { flex: 0 0 auto; width: 36px; height: 36px; display: grid; place-items: center; color: var(--rc-text); }
      .brand .mark svg { width: 32px; height: 32px; }
      /* WebP raven mark (P0 asset) — green halo mirrors the commerce nav treatment. */
      .brand .mark img { width: 34px; height: auto; display: block; object-fit: contain; filter: drop-shadow(0 0 8px var(--rc-accent-glow, rgba(86, 208, 138, 0.35))); }
      .brand .name { font-family: var(--font-display); font-weight: 600; font-size: 1.05rem; letter-spacing: -0.01em; }
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
      /* Commerce nav treatment: transparent at the top, a saturate+blur veil once
         the page scrolls past ~12px (the .is-scrolled toggle is JS-driven). */
      .topbar {
        position: sticky; top: 0; z-index: 30; height: var(--topbar-h);
        display: flex; align-items: center; gap: 14px; padding: 0 20px;
        background: transparent;
        border-bottom: 1px solid transparent;
        transition: background 0.35s var(--rc-ease, ease), border-color 0.35s var(--rc-ease, ease),
          -webkit-backdrop-filter 0.35s var(--rc-ease, ease), backdrop-filter 0.35s var(--rc-ease, ease);
      }
      .topbar.is-scrolled {
        background: rgba(7, 8, 10, 0.72);
        -webkit-backdrop-filter: saturate(160%) blur(14px);
        backdrop-filter: saturate(160%) blur(14px);
        border-bottom-color: var(--border);
      }
      [data-theme="light"] .topbar.is-scrolled { background: rgba(245, 246, 248, 0.82); }
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

      /* Hero — bounded console band, photoreal raven right-docked. Mirrors the
         standalone dashboard's .ov-hero (P2) and the commerce hero. */
      .hero { position: relative; display: grid;
        grid-template-columns: minmax(0, 1fr) clamp(180px, 26vw, 340px);
        align-items: center; gap: 28px;
        min-height: clamp(220px, 24vw, 320px);
        overflow: hidden; border-radius: var(--radius);
        padding: clamp(20px, 3vw, 44px); margin-bottom: 28px;
        border: 1px solid var(--border); box-shadow: var(--rc-shadow-sm);
        background:
          radial-gradient(120% 140% at 88% 8%, var(--rc-accent-soft, rgba(86, 208, 138, 0.14)), transparent 55%),
          linear-gradient(180deg, var(--surface-2), var(--surface)); }
      /* Signature thin teal hairline across the hero top edge (minimal accent). */
      .hero::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 2px;
        background: linear-gradient(90deg, transparent, var(--teal) 50%, transparent); opacity: 0.55; z-index: 2; }
      .hero__inner { position: relative; z-index: 1; min-width: 0; }
      .hero .pill { display: inline-flex; align-items: center; gap: 8px; font-size: 0.74rem; font-weight: 600; color: var(--teal-2); background: var(--teal-soft); border: 1px solid var(--border-strong); padding: 6px 12px; border-radius: 999px; }
      .eyebrow { display: inline-flex; align-items: center; gap: 10px; margin: 0 0 16px;
        text-transform: uppercase; letter-spacing: 0.18em; font-size: 12px; font-weight: 500; color: var(--muted); }
      .eyebrow__dot { width: 6px; height: 6px; border-radius: 50%;
        background: var(--rc-accent, #56d08a); box-shadow: 0 0 12px var(--rc-accent-glow, rgba(86, 208, 138, 0.35)); }
      .hero h1 { font-family: var(--font-display); font-weight: 600; letter-spacing: -0.025em; line-height: 1.05;
        font-size: clamp(26px, 3.4vw, 42px); margin: 0 0 14px; text-wrap: balance; }
      .hero h1 .accent { color: var(--teal-2); }
      .hero p, .hero .hero__sub { color: var(--muted); max-width: 60ch; font-size: clamp(15px, 1.4vw, 16.5px); line-height: 1.6; margin: 0; }
      .hero .hero-cta { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 24px; }
      .hero__raven { justify-self: end; align-self: center;
        width: 100%; max-width: clamp(180px, 26vw, 340px); height: auto; opacity: 0.92;
        filter: drop-shadow(0 8px 30px var(--rc-accent-glow, rgba(86, 208, 138, 0.28)));
        -webkit-mask-image: radial-gradient(closest-side, #000 78%, transparent 100%);
        mask-image: radial-gradient(closest-side, #000 78%, transparent 100%);
        user-select: none; -webkit-user-drag: none; }
      @media (max-width: 720px) {
        .hero { grid-template-columns: 1fr; }
        .hero__raven { display: none; }
      }

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
      .action-tile .t { display: block; font-weight: 600; font-size: 1rem; }
      .action-tile .d { display: block; color: var(--muted); font-size: 0.84rem; margin-top: 2px; }

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
      /* Plugin-detail filter bar: same chips as .mkt-nav, but a horizontal,
         non-sticky row that doubles as the detail page's KPI cards (icon + name
         + count + selected highlight). Clicking one filters the sections below. */
      .pd-filters { position: static; flex-direction: row; flex-wrap: wrap; gap: 8px; margin: 18px 0 6px; }
      .pd-filters button { border-color: var(--border); background: var(--surface); }
      .pd-filters button .count { margin-left: 4px; }
      .pd-filters button.active .count { color: var(--teal-2); }
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

      /* Payload mode banner — only shown above an iframe when the
         served-mode probe resolves Static. Sits above the iframe, in flow,
         so it doesn't add persistent chrome on the Live path. */
      .payload-banner { display: flex; gap: 12px; align-items: center; padding: 10px 14px; background: var(--surface); border-bottom: 1px solid var(--border-strong); color: var(--muted); font-size: 0.82rem; }
      .payload-banner .ico { display: inline-flex; }
      .payload-banner .ico svg { width: 16px; height: 16px; color: var(--teal-2); }
      .payload-banner code { font-family: var(--font-mono); font-size: 0.78rem; color: var(--text); background: var(--surface-2, var(--bg)); border: 1px solid var(--border); padding: 2px 6px; border-radius: 4px; }
      .payload-banner .msg { flex: 1; }
      .payload-banner .banner-copy { background: var(--teal); color: white; border: 0; padding: 4px 10px; border-radius: 6px; font-size: 0.78rem; cursor: pointer; }
      .payload-banner .banner-copy:hover { filter: brightness(1.05); }

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
        /* Collapse the search trigger to an icon-only button on narrow screens
           so its label can't wrap/overflow the topbar (the ⌘K palette is the
           real search surface; the opener just launches it). */
        .palette-opener { flex: 0 0 auto; width: 38px; max-width: 38px; padding: 0; gap: 0; justify-content: center; }
        .palette-opener .label, .palette-opener kbd { display: none; }
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
      .palette-opener .label { flex: 1; min-width: 0; text-align: left; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
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
      .scenario-card[data-profile="strict"].active { border-color: var(--rc-gold, #56d08a); }
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
      .pcat-row-head .pc-drift { width: 8px; height: 8px; border-radius: 50%; background: var(--rc-gold, #56d08a); }
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
      .onboarding-head .ob-raven { display: inline-flex; flex: 0 0 auto; color: var(--rc-text); }
      .onboarding-head .ob-raven svg { width: 38px; height: 38px; display: block; }
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

      /* Native-merge hosts: the dashboard + catalog sub-apps mount into these
         hidden full-width regions; the router toggles [hidden]. The !important
         keeps [hidden] authoritative over the sub-apps' own display rules. */
      [hidden] { display: none !important; }
      .payload-host { min-width: 0; }

      /* Slice B — single chrome: hide the folded dashboard's OWN category/tab
         bars (the shell sidebar's section sub-nav drives the tabs instead). The
         selector is scoped to #dash-root so the SHIPPED standalone dashboard
         (whose CSS is NOT #dash-root-scoped) keeps its own nav for consumers. */
      #dash-root .cat-bar, #dash-root .tab-bar { display: none !important; }

      /* ── Folded-in dashboard sub-app (scoped under #dash-root) ── */
      /*__DASH_CSS__*/

      /* ── Use-case lookup table (Marketplace) + rich plugin-detail cards ── */
      .uc-wrap { margin: 0 0 26px; }
      .uc-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
      .uc-table th { text-align: left; padding: 0.5rem 0.6rem; border-bottom: 1px solid var(--border); color: var(--muted); font-weight: 600; font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.04em; }
      .uc-table td { padding: 0.5rem 0.6rem; border-bottom: 1px solid var(--surface-2); vertical-align: top; }
      .uc-table tr:hover { background: var(--surface); }
      .uc-table .uc-intent { max-width: 40ch; color: var(--text); }
      .uc-table a { color: var(--teal-2); }
      .uc-table tr.uc-hidden { display: none; }
      .uc-diff { display: inline-block; padding: 0.05rem 0.45rem; border-radius: 999px; font-size: 0.7rem; border: 1px solid var(--border); color: var(--muted); }
      .uc-diff.d-starter { color: var(--ok); border-color: color-mix(in srgb, var(--ok) 40%, var(--border)); }
      .uc-diff.d-advanced { color: var(--teal-2); }
      .uc-diff.d-troubleshooting { color: var(--danger); }
      .scn { border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; margin: 8px 0; background: var(--surface); }
      .scn .scn-i { font-size: 0.86rem; margin-bottom: 4px; }
      .scn .scn-t { font-size: 0.8rem; color: var(--muted); margin-bottom: 3px; }
      .scn .scn-o { font-size: 0.8rem; color: var(--muted); }
      .qs { margin: 6px 0 0; padding-left: 1.1rem; }
      .qs li { font-size: 0.82rem; color: var(--muted); margin-bottom: 2px; }
      .ref-item { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; box-shadow: var(--rc-shadow-sm); }
      .ref-item .ri-n { font-family: var(--font-mono); font-size: 0.86rem; }
      .ref-item .ri-d { color: var(--muted); font-size: 0.82rem; margin-top: 4px; }
      /* Decision-tree dropdowns on a plugin detail page (moved off the dashboard
         Guidance tab). Collapsed by default so the page stays light. */
      .dt-tree-intro { color: var(--muted); font-size: 0.85rem; margin: 0 0 12px; }
      .dt-tree-list { display: flex; flex-direction: column; gap: 8px; }
      .dt-tree { border: 1px solid var(--border); border-radius: 8px; background: var(--surface); overflow: hidden; }
      .dt-tree-summary { display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap; cursor: pointer; padding: 11px 14px; list-style: none; user-select: none; }
      .dt-tree-summary::-webkit-details-marker { display: none; }
      .dt-tree-summary::before { content: "\\25B8"; color: var(--accent); font-size: 0.7rem; line-height: 1.4; }
      .dt-tree[open] > .dt-tree-summary::before { content: "\\25BE"; }
      .dt-tree-title { font-weight: 600; font-size: 0.9rem; }
      .dt-tree-when { color: var(--muted); font-size: 0.8rem; }
      .dt-tree-svg { padding: 8px 14px 16px; overflow-x: auto; border-top: 1px solid var(--border); }
      .dt-tree-svg svg, .dt-tree-img { max-width: 100%; height: auto; display: block; }
    </style>
  </head>
  <body>
    <div class="scrim" id="scrim" aria-hidden="true"></div>
    <div class="app">
      <!-- ======================= SIDEBAR ======================= -->
      <aside class="sidebar" id="sidebar">
        <div class="brand">
          <span class="mark" aria-hidden="true">__RAVEN_MARK_IMG__</span>
          <span class="meta">
            <span class="name">Raven<b>Claude</b></span>
            <span class="tag">Engineering Team Platform</span>
          </span>
        </div>
        <nav class="nav" id="primary-nav" aria-label="Primary"><a href="#/control" data-nav="control">Control</a><a href="#/activity" data-nav="activity">Activity</a><a href="#/guardrails" data-nav="guardrails">Guardrails</a><a href="#/catalog" data-nav="catalog">Catalog</a></nav>
        <div class="sidebar-foot">
          <div>v<span id="foot-version">__MKT_VERSION__</span></div>
          <div class="detail">Updated __GENERATED__</div>
          <div class="detail"><a href="pitch.html">What is RavenClaude?</a></div>
          <div class="detail"><a href="https://ravenpower.net" target="_blank" rel="noopener noreferrer">Raven Power ↗</a></div>
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
            <a class="btn ghost hide-sm" href="#/discover"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>Use cases</a>
            <a class="btn primary" href="#/discover"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3h18v4H3z"/><path d="M5 7v12h14V7"/><path d="M9 11h6"/></svg>Browse Plugins</a>
          </div>
        </header>
        <main class="content" id="view" tabindex="-1"></main>
        <!-- Native-merged sub-apps. Mounted once, hidden until routed to.
             INVARIANT: these are trusted, same-org generated artifacts folded
             into this document (not iframes) — their live /__* fetches run at
             this page's origin when served by serve-dashboards.py. -->
        <div class="content payload-host" id="dash-root" hidden><!--__DASH_BODY__--></div>
        <!-- Decision-tree store: every plugin's pre-rendered tree diagrams,
             inlined once and hidden. The plugin detail view (__openPlugin) clones
             the matching plugin's trees into collapsible dropdowns. This is the
             trees' only home in the portal — they were moved off the dashboard
             Guidance tab so each tree lives next to the plugin it guides. -->
        <div id="dt-store" hidden><!--__DT_STORE__--></div>
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

    <!-- Folded-in dashboard sub-app. Loaded BEFORE the shell router so
         window.__dashApp exists when route() first runs. IIFE-wrapped so its
         globals (svg/toast/esc…) can't collide with the shell's. -->
    <script>
      /*__DASH_JS__*/
    </script>

    <!-- Lazy detail island (H4 / plan §1.4). The detail-only fields read SOLELY by
         window.__openPlugin — agents[].scenarios/.quickstart/.works_with and
         plugins[].scripts_index/.scenarios_index/.templates_index/.best_practices_index
         — are parked here as inert application/json so they never sit on the eager
         window.__RC_DATA__ JS-parse path (~1.28 MB off it, zero content loss).
         hydrateDetail() merges them back on demand and THROWS if this element is
         renamed / missing / unparseable or lacks the plugin's record — the
         silent-empty-section is the exact H4 failure it guards. <script> contents
         are CDATA, so this is DOM-budget-neutral (the +1 element is offset by
         folding the former standalone window.__RC_DATA__ <script> into the shell
         script below, -1). -->
    <script type="application/json" id="plugin-detail-payload">/*__PLUGIN_DETAIL_PAYLOAD__*/</script>
    <script>
      "use strict";
      // window.__RC_DATA__ and the shell that reads it share ONE <script> so the
      // detail island above is DOM-count-neutral. "use strict" stays the FIRST
      // statement so strict mode still governs the whole shell.
      window.__RC_DATA__ = /*__RC_DATA__*/;
      const D = window.__RC_DATA__;
      const $ = (s, r = document) => r.querySelector(s);
      const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
      const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
      const byName = (n) => D.plugins.find((p) => p.name === n);

      /* ---- Lazy detail island — H4 hydration contract (plan §1.4) -------------
       * The detail-only fields (agents[].scenarios/.quickstart/.works_with +
       * plugins[].scripts_index/.scenarios_index/.templates_index/.best_practices_index)
       * live in <script id="plugin-detail-payload"> to keep them off the eager
       * __RC_DATA__ parse path. KEY PRESENCE is the hydration sentinel: an eager
       * record does NOT carry these keys, so ABSENT means "not hydrated" and []
       * means "genuinely zero". hydrateDetail() merges the island fields back onto
       * a record BEFORE __openPlugin counts/filters them, and THROWS — never
       * silently renders an empty section (that IS the H4 failure) — if the island
       * element is renamed/missing, unparseable, or has no record for this plugin. */
      let __detailIsland;
      function __loadDetailIsland() {
        if (__detailIsland) return __detailIsland;
        const el = document.getElementById("plugin-detail-payload");
        if (!el) throw new Error("hydrateDetail: #plugin-detail-payload island element is missing");
        try {
          __detailIsland = JSON.parse(el.textContent);
        } catch (e) {
          throw new Error("hydrateDetail: #plugin-detail-payload island is unparseable — " + e.message);
        }
        return __detailIsland;
      }
      function hydrateDetail(p) {
        if (!p) return p; // unknown plugin name — not a hydration failure; caller returns
        const rec = (__loadDetailIsland().plugins || {})[p.name];
        if (!rec) throw new Error("hydrateDetail: island has no record for plugin '" + p.name + "'");
        // Plugin-level islanded fields (explicit — never clobber the eager p.agents list).
        p.scripts_index = rec.scripts_index;
        p.scenarios_index = rec.scenarios_index;
        p.templates_index = rec.templates_index;
        p.best_practices_index = rec.best_practices_index;
        // Agent-level islanded subfields (scenarios/quickstart/works_with), by name.
        const arecs = rec.agents || {};
        (p.agents || []).forEach((a) => { const ar = arecs[a.name]; if (ar) Object.assign(a, ar); });
        // Free secondary invariant (measured: 0 mismatches across all 167 plugins):
        // the eager counts MUST agree with the hydrated index lengths. Do NOT extend
        // to templates (4 mismatches) or best_practices (no eager count) — plan §1.4.
        if (p.counts.tools !== (p.scripts_index || []).length ||
            p.counts.scenarios !== (p.scenarios_index || []).length) {
          throw new Error("hydrateDetail: eager-count vs island-length mismatch for '" + p.name + "'");
        }
        return p;
      }

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
        { id: "control", label: "Control", icon: "sliders" },
        { id: "activity", label: "Activity", icon: "chart" },
        { id: "guardrails", label: "Guardrails", icon: "shield" },
        { id: "catalog", label: "Catalog", icon: "market" },
      ];

      // ── 6-section task IA + native-merged dashboard routing (Slice A) ──
      // Sidebar = Home · Discover · Configure · Observe · Act · Learn. The dashboard
      // content is folded into THIS document (no iframes): mounted in #dash-root,
      // shown by toggling [hidden], driven via window.__dashApp.show(). Every
      // legacy route still resolves via SECTION_ALIAS (old shell top-level) +
      // DASH_OWNER (dashboard tab → owning section). (Slice A keeps the dashboard's
      // own cat-bar/tab-bar visible; Slice B hides it + adds a shell sub-nav.)
      // INVARIANT: this payload is a trusted, same-org generated artifact — its
      // live /__* fetches run at this page's origin when served by serve-dashboards.py.
      const DASH_SECTIONS = new Set([
        "heimdall", "vidarr", "norns", "nidhoggr", "bifrost", "mimir",
        "sleipnir", "saga", "activity", "learn", "web-access", "pipeline",
        "comfort-posture", "dashboard", "settings", "overview", "install",
        "simulator", "commands", "trees", "about",
      ]);
      // Route name → real dashboard tab id where they differ (incl. the two
      // phantom routes: nidhoggr is a card in heimdall, sleipnir a banner in activity).
      const DASH_TAB_ALIAS = {
        dashboard: "activity", "comfort-posture": "settings",
        nidhoggr: "heimdall", sleipnir: "activity", concepts: "learn",
        // P4 (dashboard-consumption): the Observe family is physically merged, so
        // these retired tab routes now resolve to their destination FRAGMENT tab —
        // Activity (saga/mimir/streams/norns) or Guardrails/Heimdall (vidarr). Each
        // value is a real .tab-btn[data-tab] (Gate 51's DASH_TAB_ALIAS-target check).
        saga: "activity", mimir: "activity", streams: "activity",
        norns: "activity", vidarr: "heimdall",
        // P5 (dashboard-consumption): install/bifrost/about/commands were folded into
        // the Help drawer (panel-help, data-tab="help"), so their retired tab routes
        // resolve to the "help" FRAGMENT tab. "dashboard" was retargeted off the
        // deleted "overview" tab to "activity" (it is aliased to activity anyway).
        about: "help", install: "help", bifrost: "help", commands: "help",
      };
      // Retired Observe sub-routes now live as anchored <section>s inside a destination
      // tab (P4). A bare #/saga etc. has no sub-segment, so map the route name → its
      // in-panel anchor id; viewDashboard passes it through activate()'s `sub`, which
      // scrolls to it inside Activity/Guardrails. nidhoggr/sleipnir keep their existing
      // in-panel mounts (the debt card / the stables banner).
      const DASH_ANCHOR = {
        saga: "saga", mimir: "mimir", streams: "streams", norns: "norns",
        vidarr: "vidarr", nidhoggr: "heimdall-debt", sleipnir: "sleipnir-stables",
      };
      // Legacy top-level shell route → canonical NAV section (back-compat for
      // committed bookmarks, ⌘K quick-actions, and internal hrefs).
      const SECTION_ALIAS = {
        marketplace: "catalog", team: "catalog", "repo-guide": "catalog",
        discover: "catalog", configuration: "control", resources: "catalog",
        dashboard: "activity", home: "control",
        // P5 (dashboard-consumption): the retired shell views resolve to Control as
        // NAMED removals — #/configure (the deleted non-writing posture editor) and
        // #/overview / #/simulator (deleted tabs) land on Settings (the real editor).
        configure: "control", overview: "control", simulator: "control",
      };
      // LEGACY_VIEW retired (P5, dashboard-consumption): viewTeam was deleted, so no
      // own-view legacy route remains — #/team resolves via SECTION_ALIAS (team→catalog).
      // Dashboard tab route → the NAV section that owns it (for highlight + dispatch).
      const DASH_OWNER = {
        heimdall: "guardrails", vidarr: "guardrails", nidhoggr: "guardrails",
        norns: "activity", mimir: "activity", saga: "activity", activity: "activity",
        streams: "activity", sleipnir: "activity",
        settings: "control", "comfort-posture": "control", "web-access": "control",
        pipeline: "control",
        // P5: overview/simulator tabs deleted (resolve via SECTION_ALIAS → Control);
        // the Help drawer (install/bifrost/about/commands + help) is owned by Catalog.
        "plugin-vars": "catalog", commands: "catalog", trees: "catalog", bifrost: "catalog",
        install: "catalog", about: "catalog", concepts: "catalog", help: "catalog",
      };
      // SECTION_TABS retired (P3, dashboard-consumption). The 6-section IA's
      // per-section sub-nav is gone: the shell now has four task destinations
      // (Control / Activity / Guardrails / Catalog) whose dashboard tabs are
      // reached directly through DASH_OWNER + route(), not a section sub-nav.
      // Kept as an empty object literal so navChildren()'s guard is a no-op and
      // the two Gate-51 parsers (which anchor on the SECTION_TABS declaration)
      // still slice it cleanly, finding zero sub-nav routes — which is correct.
      const SECTION_TABS = {};
      function payloadKind(section) {
        // A dashboard-owned tab route (drives the #dash-root host). Bare "learn"
        // is intercepted by the NAV check in route() before this, so the Learn
        // section wins #/learn; the concepts tab is reached inside the Learn area.
        if (DASH_OWNER[section]) return "dashboard";
        return null;
      }
      function showHost(which) {
        // which ∈ {"view","dash"} — exactly one host is visible.
        $("#view").hidden = which !== "view";
        const dr = $("#dash-root"); if (dr) dr.hidden = which !== "dash";
      }
      // Served-mode probe: one cached HEAD to /__csrf (the same same-origin signal
      // the dashboard's own CSRF bootstrap uses — the parity gate guards that the
      // endpoint exists). The cross-origin/404 reject on a static GitHub-Pages host
      // IS the "static" signal; we never add Access-Control-Allow-Origin (that
      // would break the DNS-rebinding defense). Tri-state: null=unknown,
      // true=served (127.0.0.1), false=static.
      let _served = null, _servedP = null;
      function probeServed() {
        if (_servedP) return _servedP;
        _servedP = new Promise((resolve) => {
          const ctl = (typeof AbortController === "function") ? new AbortController() : null;
          const t = setTimeout(() => { try { ctl && ctl.abort(); } catch (_) {} }, 600);
          fetch("/__csrf", { method: "HEAD", signal: ctl ? ctl.signal : undefined })
            .then((r) => { clearTimeout(t); _served = !!(r && r.ok); resolve(_served); })
            .catch(() => { clearTimeout(t); _served = false; resolve(false); });
        });
        return _servedP;
      }
      const SERVED_CMD = "rc dashboard";
      function setServedBanner(live) {
        const host = $("#dash-root"); if (!host) return;
        const existing = host.querySelector(".payload-banner");
        if (!live || _served !== false) { if (existing) existing.remove(); return; }
        if (existing) return;
        host.insertAdjacentHTML("afterbegin",
          `<div class="payload-banner" role="status" aria-live="polite"><span class="ico">${svg("info")}</span><span class="msg">Live data needs the served dashboard — run <code>${esc(SERVED_CMD)}</code>.</span><button type="button" class="banner-copy" data-cmd="${esc(SERVED_CMD)}">Copy</button></div>`);
        const b = host.querySelector(".payload-banner .banner-copy");
        if (b) b.addEventListener("click", () => window.__copy(b.dataset.cmd || SERVED_CMD, "Command"));
      }
      function reprobeServed() {
        // probeServed() is memoized for the page's life. A detached, session-
        // outliving dashboard server can be stopped (--stop) or idle-expire
        // (--max-idle) while this tab stays open; on regaining visibility/focus,
        // re-run the probe so a dead loopback server surfaces the "run the command"
        // banner (the exact command to run) instead of a stale served state — and a
        // restarted server clears it, recovering without a manual reload (E4/L4).
        _served = null;
        _servedP = null;
        probeServed().then(() => {
          const cur = location.hash.replace(/^#\/?/, "").split("/")[0];
          const owner = DASH_OWNER[cur] || SECTION_ALIAS[cur] || cur;
          const live = ["control", "activity", "guardrails"].includes(owner);
          setServedBanner(live);
        });
      }
      function viewDashboard(section, sub) {
        showHost("dash");
        // A retired Observe route (#/saga … #/nidhoggr) carries no sub-segment; map it
        // to its in-panel anchor id so activate() scrolls to the merged section (P4).
        const anchor = sub || DASH_ANCHOR[section];
        if (window.__dashApp) window.__dashApp.show(DASH_TAB_ALIAS[section] || section, anchor);
        // Banner only on live-data destinations (Activity + Guardrails + Control);
        // the Catalog/Help-area dashboard tabs work offline, so no banner there.
        const owner = DASH_OWNER[section] || "activity";
        const live = owner === "activity" || owner === "guardrails" || owner === "control";
        if (_served !== null) setServedBanner(live);
        else probeServed().then(() => {
          const cur = location.hash.replace(/^#\/?/, "").split("/")[0];
          const stillDash = DASH_OWNER[cur] || ["control", "activity", "guardrails"].includes(cur) || ["control", "activity", "guardrails"].includes(SECTION_ALIAS[cur]);
          if (stillDash) setServedBanner(live);
        });
      }
      // Subcategories live under the one section the repo actually has a
      // hierarchy for: Marketplace → plugin categories (existing #/discover/<cat>
      // routes). The accordion only renders under the ACTIVE top item, and only
      // when the sidebar is expanded (CSS hides .nav-sub when collapsed).
      function navChildren(id) {
        // Catalog keeps the plugin-category accordion (the old Discover sub-nav):
        // Specialists + one entry per plugin category. Deep-links (#/team,
        // #/discover/<cat>) still resolve through the router. The other three
        // destinations have no sub-nav (SECTION_TABS retired in P3).
        if (id === "catalog" && D.categories) {
          const counts = {};
          D.plugins.forEach((p) => { counts[p.category] = (counts[p.category] || 0) + 1; });
          const top = location.hash.replace(/^#\/?/, "").split("/")[0];
          const onTeam = top === "team";
          const cur = (location.hash.split("/")[2] || "all");
          const items = [`<a class="nav-subitem${onTeam ? " active" : ""}" href="#/team">Specialists</a>`];
          items.push(
            ...[{ id: "all", label: "All plugins", count: D.plugins.length }]
              .concat(D.categories.map((c) => ({ id: c.id, label: c.label, count: counts[c.id] || 0 })))
              .map((c) => `<a class="nav-subitem${!onTeam && c.id === cur ? " active" : ""}" href="#/discover/${c.id === "all" ? "" : c.id}">${esc(c.label)}<span class="count">${c.count}</span></a>`),
          );
          return items.join("");
        }
        return "";
      }
      function renderNav(active) {
        $("#primary-nav").innerHTML =
          '<div class="group-label">Platform</div>' +
          NAV.map((n) => {
            const item = `<a class="nav-item${n.id === active ? " active" : ""}" href="#/${n.route || n.id}" data-nav="${n.id}"${n.id === active ? ' aria-current="page"' : ""}>${svg(n.icon)}<span class="label">${n.label}</span></a>`;
            const subs = n.id === active ? navChildren(n.id) : "";
            return subs ? `${item}<div class="nav-sub">${subs}</div>` : item;
          }).join("");
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
        { id: 1, title: "Pick a posture scenario", desc: "Recommended: Client Delivery", cta: "Open", action: "route", route: "#/configure" },
        { id: 2, title: "Read GETTING_STARTED.md", desc: "10-minute canonical walkthrough", cta: "Open", action: "href", href: "GETTING_STARTED.md" },
        { id: 3, title: "Run your first /spawn-team", desc: "Copy an example prompt", cta: "Copy", action: "copyCmd", cmd: "/spawn-team architect → coder → tester for: <describe your change>" },
        { id: 4, title: "Open the deep posture dashboard", desc: "rc dashboard — Save & apply writes .ravenclaude/comfort-posture.yaml", cta: "Copy", action: "copyCmd", cmd: "rc dashboard" },
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
            <span class="ob-raven" aria-hidden="true">__RAVEN_LOGO_SVG__</span>
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

      /* ---------------- Retired shell views (P5, dashboard-consumption) ----------------
         viewHome (marketing hero + CTA grid + onboarding checklist), viewTeam (specialist
         roster; + the allAgents helper) and viewConfiguration (the SECOND, non-writing
         posture editor — incl. its 167 always-`checked` "Plugin activation" toggles wired
         to nothing, a straight defect removal) were DELETED. #/home and #/configure now
         resolve to Control (panel-settings, the one editor that writes) and #/team to
         Catalog, via SECTION_ALIAS; route()'s default is Control. See
         docs/dashboard-removed-routes.md. */

      /* ---------------- MARKETPLACE ---------------- */
      let mktState = { cat: "all", q: "" };
      function viewMarketplace(catId) {
        mktState.cat = catId || "all";
        const cats = D.categories;
        const counts = {};
        D.plugins.forEach((p) => { counts[p.category] = (counts[p.category] || 0) + 1; });
        const navBtns = `<button data-cat="all" class="${mktState.cat === "all" ? "active" : ""}">${svg("market")} All plugins <span class="count">${D.plugins.length}</span></button>` +
          cats.map((c) => `<button data-cat="${c.id}" class="${mktState.cat === c.id ? "active" : ""}">${svg(c.icon)} ${esc(c.label)} <span class="count">${counts[c.id] || 0}</span></button>`).join("");

        const featured = D.featured.map((f) => {
          const plugins = f.plugins.map(byName).filter(Boolean);
          const tags = plugins.map((p) => `<span class="chip teal">${esc(p.label)}</span>`).join("");
          const total = plugins.reduce((n, p) => n + p.counts.agents, 0);
          return `<div class="card"><div style="font-weight:700">${esc(f.title)}</div>
            <p class="desc" style="color:var(--muted);font-size:.86rem;margin:8px 0 0">${esc(f.blurb)}</p>
            <div class="tags">${tags}</div>
            <div class="metrics" style="margin-top:12px;font-size:.76rem;color:var(--faint)"><span><b style="color:var(--teal-2)">${total}</b> specialists combined</span></div>
            <div class="pc-foot" style="margin-top:14px"><a class="btn" href="#/discover">View in marketplace</a></div></div>`;
        }).join("");

        $("#view").innerHTML = `
          <div class="page-head"><span class="eyebrow">Marketplace</span><h1>Browse the plugin catalog</h1>
            <p class="lede" style="max-width:none">${D.plugins.length} ready-made plugins, sorted by topic. Each one comes with expert agents, skills they can use, and a built-in pile of know-how. Start from <em>what you want to do</em>, or pick a group below.</p></div>
          <details class="uc-wrap card" style="padding:14px 16px">
            <summary style="cursor:pointer;font-weight:600">I want to… <span class="count">${D.use_cases.length}</span> <span style="color:var(--muted);font-weight:400;font-size:.85rem">— go from a task to the agent + plugin that does it</span></summary>
            <input type="search" id="uc-q" placeholder="What do you want to do? e.g. “forecast cash”, “review Apex”, “set up auth”…" aria-label="Search use cases" style="width:100%;margin-top:10px;background:var(--surface);border:1px solid var(--border);color:var(--text);padding:.55rem .8rem;border-radius:8px" />
            <div style="max-height:360px;overflow:auto;margin-top:10px">
              <table class="uc-table"><thead><tr><th>I want to…</th><th>Agent</th><th>Plugin</th><th>Level</th></tr></thead><tbody id="uc-body"></tbody></table>
            </div>
          </details>
          <div class="mkt-filters">
            <input type="search" id="mkt-q" placeholder="Search plugins by name, description or technology…" value="${esc(mktState.q)}" aria-label="Search plugins" />
          </div>
          <div class="mkt">
            <nav class="mkt-nav" id="mkt-nav" aria-label="Plugin categories">${navBtns}</nav>
            <div id="mkt-grid"></div>
          </div>
          <div class="section-title" style="margin-top:28px"><h2>Featured plugin combinations</h2><span class="hint">teams that work well together</span></div>
          <div class="grid cols-2">${featured}</div>`;

        function renderUC(q) {
          q = (q || "").toLowerCase().trim();
          const rows = (D.use_cases || []).filter((u) => !q || (u.intent + " " + u.agent + " " + u.plugin_label + " " + u.audience).toLowerCase().includes(q)).slice(0, 400);
          $("#uc-body").innerHTML = rows.map((u) => `<tr>
            <td class="uc-intent">${esc(u.intent)}</td>
            <td><code>${esc(u.agent)}</code></td>
            <td><a href="#/discover" onclick="window.__openPlugin('${esc(u.plugin)}');return false">${esc(u.plugin_label)}</a></td>
            <td><span class="uc-diff d-${esc(u.difficulty)}">${esc(u.difficulty)}</span></td>
          </tr>`).join("") || `<tr><td colspan="4" style="color:var(--muted);padding:12px">No use case matches “${esc(q)}”.</td></tr>`;
        }
        renderUC("");
        $("#uc-q").addEventListener("input", (e) => renderUC(e.target.value));

        function pluginCard(p) {
          const reqs = (p.requires || []).length ? `<span class="chip">requires core</span>` : "";
          return `<div class="card plugin-card">
            <div class="pc-head"><span class="ico" style="width:34px;height:34px;border-radius:9px;display:grid;place-items:center;background:var(--teal-soft);color:var(--teal-2);border:1px solid var(--border-strong)">${svg((cats.find((c) => c.id === p.category) || {}).icon || "sparkle")}</span><span class="nm">${esc(p.label)}</span><span class="ver">v${esc(p.version)}</span></div>
            <p class="desc">${esc(p.short)}</p>
            <div class="metrics"><span><b>${p.counts.agents}</b> specialists</span><span><b>${p.counts.skills}</b> skills</span><span><b>${p.counts.knowledge}</b> knowledge docs</span>${p.counts.scenarios ? `<span><b>${p.counts.scenarios}</b> scenarios</span>` : ""}${p.counts.tools ? `<span><b>${p.counts.tools}</b> tools</span>` : ""}</div>
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
          if (mktState.cat === "all") { history.replaceState(null, "", "#/discover"); } else { history.replaceState(null, "", "#/discover/" + mktState.cat); }
          renderGrid();
        });
        $("#mkt-q").addEventListener("input", (e) => { mktState.q = e.target.value; renderGrid(); });
        renderGrid();
      }
      // Rich per-plugin REFERENCE (the former repo-guide card, folded in): agents
      // with example scenarios / quickstart / audience / works-with, plus
      // skills / runnable tools / scenarios / hooks / rules / templates /
      // best-practices. There is no per-plugin variable editor in the portal, so
      // the detail hero's "Configure agents" button points at the global
      // comfort-posture editor (#/configure); the legacy #/plugin-* route still
      // resolves here for bookmarked/back-forward deep-links.
      window.__openPlugin = function (name) {
        // Hydrate the detail-only island fields BEFORE building sectionDefs — if
        // the plugin exists, hydrateDetail throws on a hydration failure (never
        // renders a silent-empty section); an unknown name returns falsy and we exit.
        const p = hydrateDetail(byName(name)); if (!p) return;
        showHost("view");
        const cats = D.categories;
        const catLabel = (cats.find((c) => c.id === p.category) || {}).label || "Marketplace";
        const diffCls = (d) => "d-" + (d || "starter");
        const scn = (a) => {
          if (!a.scenarios || !a.scenarios.length) return "";
          const first = a.scenarios.find((x) => x.difficulty === "starter") || a.scenarios[0];
          const rest = a.scenarios.filter((x) => x !== first);
          const one = (x) => `<div class="scn"><div class="scn-i"><b>Intent:</b> ${esc(x.intent)}</div>${x.trigger_phrase ? `<div class="scn-t">You type: <code>${esc(x.trigger_phrase)}</code></div>` : ""}${x.outcome ? `<div class="scn-o">You get: ${esc(x.outcome)}</div>` : ""}<span class="uc-diff ${diffCls(x.difficulty)}" style="margin-top:6px">${esc(x.difficulty)}</span></div>`;
          return `<div style="margin-top:8px"><div class="ri-d" style="text-transform:uppercase;letter-spacing:.04em;font-size:.7rem">Example scenario${a.scenarios.length > 1 ? "s" : ""}</div>${one(first)}${rest.length ? `<details><summary style="cursor:pointer;font-size:.8rem;color:var(--muted)">+ ${rest.length} more</summary>${rest.map(one).join("")}</details>` : ""}</div>`;
        };
        const qs = (a) => (a.quickstart && a.quickstart.length) ? `<div style="margin-top:8px"><div class="ri-d" style="text-transform:uppercase;letter-spacing:.04em;font-size:.7rem">Quickstart</div><ol class="qs">${a.quickstart.map((q) => `<li>${esc(q)}</li>`).join("")}</ol></div>` : "";
        const aud = (a) => (a.audience && a.audience.length) ? `<div class="tags" style="margin:6px 0">${a.audience.map((x) => `<span class="chip">${esc(x)}</span>`).join("")}</div>` : "";
        const ww = (a) => (a.works_with && a.works_with.length) ? `<div style="margin-top:8px;font-size:.8rem;color:var(--muted)">Works well with: ${a.works_with.map((x) => `<span class="chip">${esc(x)}</span>`).join(" ")}</div>` : "";
        const agents = p.agents.map((a) => `<div class="card" style="padding:14px">
          <div style="display:flex;align-items:baseline;gap:8px"><span class="nm" style="font-weight:600">${esc(a.label)}</span>${a.model ? `<span class="chip">${esc(a.model)}</span>` : ""}</div>
          ${aud(a)}<div class="desc" style="color:var(--muted);font-size:.85rem">${esc(a.description || "")}</div>${scn(a)}${qs(a)}${ww(a)}
        </div>`).join("");
        const named = (i) => `<div class="ref-item"><div class="ri-n">${esc(i.name)}</div>${i.description ? `<div class="ri-d">${esc(i.description)}</div>` : ""}</div>`;
        const hookItem = (i) => `<div class="ref-item"><div class="ri-n">${esc(i.name)} ${i.event ? `<span class="chip">${esc(i.event)}</span>` : ""}</div>${i.description ? `<div class="ri-d">${esc(i.description)}</div>` : ""}</div>`;
        const refGrid = (title, items, fmt) => (items && items.length) ? `<div class="section-title"><h2>${title} <span class="hint">${items.length}</span></h2></div><div class="grid cols-2">${items.map(fmt).join("")}</div>` : "";
        const scnItem = (i) => `<div class="ref-item"><div class="ri-n">${esc(i.name)}${i.description ? ` <span class="chip">${esc(i.description)}</span>` : ""}</div></div>`;
        const toolItem = (i) => `<div class="ref-item"><div class="ri-n"><code>${esc(i.name)}</code>${(i.modes || []).map((m) => `<span class="chip">${esc(m)}</span>`).join(" ")}</div>${i.purpose ? `<div class="ri-d">${esc(i.purpose)}</div>` : ""}</div>`;
        // Decision trees for THIS plugin: pulled from the hidden #dt-store, each
        // rendered as a collapsible dropdown with its pre-rendered Mermaid SVG.
        const trees = (() => {
          const store = document.getElementById("dt-store");
          // #dt-store is emitted UNCONDITIONALLY (plan §1.3), so its absence is
          // never legitimate — throw rather than silently drop the trees section.
          if (!store) throw new Error("dt-store missing");
          const mine = Array.from(store.querySelectorAll('.dt-item[data-plugin="' + (window.CSS && CSS.escape ? CSS.escape(name) : name) + '"]'));
          // A plugin with no trees is the legitimate empty case — stay silent.
          if (!mine.length) return { count: 0, html: "" };
          const one = (el) => {
            const title = el.getAttribute("data-title") || "Decision tree";
            const when = el.getAttribute("data-when") || "";
            const src = el.getAttribute("data-svg") || "";
            // Lazy <img> — the browser fetches the SVG only when this <details> is
            // opened/scrolled near, so the portal never ships 600+ inlined diagrams.
            const img = src ? `<img loading="lazy" decoding="async" src="${esc(src)}" alt="${esc(title)} decision tree" class="dt-tree-img">` : "";
            return `<details class="dt-tree"><summary class="dt-tree-summary"><span class="dt-tree-title">${esc(title)}</span>${when ? `<span class="dt-tree-when">${esc(when)}</span>` : ""}</summary><div class="dt-tree-svg">${img}</div></details>`;
          };
          return { count: mine.length, html: `<div class="section-title"><h2>Decision trees <span class="hint">${mine.length}</span></h2></div><p class="dt-tree-intro">When-this-applies guidance these agents follow. Click to expand each flow.</p><div class="dt-tree-list">${mine.map(one).join("")}</div>` };
        })();
        // Each content area is a filterable section: build a def list (icon +
        // label + count + body), render the KPI/filter chips from it, and wrap
        // each body in a [data-pdsec] container the chip click handler toggles.
        const specialistsBody = agents ? `<div class="section-title"><h2>Specialists <span class="hint">${p.agents.length}</span></h2></div><div class="grid cols-2">${agents}</div>` : "";
        const sectionDefs = [
          { id: "agents", icon: "team", label: "Specialists", count: p.agents.length, body: specialistsBody },
          { id: "skills", icon: "spark", label: "Skills", count: (p.skills_index || []).length, body: refGrid("Skills", p.skills_index, named) },
          { id: "tools", icon: "sliders", label: "Tools", count: (p.scripts_index || []).length, body: refGrid("Runnable tools", p.scripts_index, toolItem) },
          { id: "scenarios", icon: "book", label: "Scenarios", count: (p.scenarios_index || []).length, body: refGrid("Scenario field notes", p.scenarios_index, scnItem) },
          { id: "hooks", icon: "shield", label: "Hooks", count: (p.hooks_index || []).length, body: refGrid("Hooks", p.hooks_index, hookItem) },
          { id: "rules", icon: "check", label: "Rules", count: (p.rules_index || []).length, body: refGrid("Rules", p.rules_index, named) },
          { id: "templates", icon: "copy", label: "Templates", count: (p.templates_index || []).length, body: refGrid("Templates", p.templates_index, named) },
          { id: "practices", icon: "sparkle", label: "Best practices", count: (p.best_practices_index || []).length, body: refGrid("Best practices", p.best_practices_index, named) },
          { id: "trees", icon: "tree", label: "Decision trees", count: trees.count, body: trees.html },
        ].filter((s) => s.body);
        const pdNav = `<button data-sec="all" class="active">${svg("market")} All <span class="count">${sectionDefs.reduce((n, s) => n + s.count, 0)}</span></button>` +
          sectionDefs.map((s) => `<button data-sec="${s.id}">${svg(s.icon)} ${esc(s.label)} <span class="count">${s.count}</span></button>`).join("");
        const pdBody = sectionDefs.map((s) => `<div data-pdsec="${s.id}">${s.body}</div>`).join("");
        $("#view").innerHTML = `
          <a class="btn ghost" href="#/discover/${p.category}" style="margin-bottom:18px">← Back to ${esc(catLabel)}</a>
          <div class="page-head"><span class="eyebrow">${esc(p.category_label)}</span><h1>${esc(p.label)} <span style="font-family:var(--font-mono);font-size:1rem;color:var(--faint)">v${esc(p.version)}</span></h1>
            <p class="lede" style="max-width:none">${esc(p.description)}</p>
            <div class="hero-cta" style="margin-top:16px;display:flex;gap:10px;flex-wrap:wrap">
              <button class="btn primary" type="button" onclick="window.__copy('/plugin install ${esc(p.name)}@ravenclaude','Install command')">${svg("plus")} Copy install command</button>
              <a class="btn" href="#/plugin-vars/${esc(p.name)}">${svg("sliders")} Edit variables</a>
              <a class="btn" href="#/configure">${svg("sliders")} Configure agents</a>
            </div></div>
          <nav class="mkt-nav pd-filters" id="pd-filters" aria-label="Filter this plugin's contents">${pdNav}</nav>
          ${p.requires && p.requires.length ? `<div class="callout" style="margin-top:14px">${svg("info")}<span>Requires ${p.requires.map((r) => `<code>${esc(r)}</code>`).join(", ")}</span></div>` : ""}
          ${pdBody}
          <div class="tags" style="margin-top:20px">${p.keywords.map((k) => `<span class="chip">${esc(k)}</span>`).join("")}</div>`;
        // Wire the KPI/filter chips: clicking one shows only its section
        // ("All" restores everything); the active chip carries the highlight.
        const pdf = $("#pd-filters");
        if (pdf) pdf.addEventListener("click", (e) => {
          const b = e.target.closest("button"); if (!b) return;
          const sel = b.dataset.sec;
          $$("#pd-filters button").forEach((x) => x.classList.toggle("active", x === b));
          $$("[data-pdsec]").forEach((el) => { el.style.display = (sel === "all" || el.dataset.pdsec === sel) ? "" : "none"; });
        });
        $("#view").focus();
        window.scrollTo({ top: 0, behavior: "smooth" });
      };

      /* ---------------- RESOURCES ---------------- */
      function viewResources() {
        const s = D.stats;
        const totalTemplates = D.plugins.reduce((n, p) => n + p.counts.templates, 0);
        const totalKnowledge = D.plugins.reduce((n, p) => n + p.counts.knowledge, 0);
        const templateCards = D.plugins.filter((p) => p.counts.templates).sort((a, b) => b.counts.templates - a.counts.templates).map((p) => `
          <div class="card"><div style="display:flex;align-items:center;gap:8px"><span style="color:var(--teal-2)">${svg("book")}</span><b>${esc(p.label)}</b><span class="ver" style="margin-left:auto;font-family:var(--font-mono);font-size:.72rem;color:var(--faint)">${p.counts.templates} templates</span></div><p style="color:var(--muted);font-size:.82rem;margin:8px 0 0">${esc(p.short)}</p></div>`).join("");
        const treeCards = D.plugins.filter((p) => p.counts.knowledge).sort((a, b) => b.counts.knowledge - a.counts.knowledge).slice(0, 9).map((p) => `
          <div class="card"><div style="display:flex;align-items:center;gap:8px"><span style="color:var(--teal-2)">${svg("tree")}</span><b>${esc(p.label)}</b><span class="ver" style="margin-left:auto;font-family:var(--font-mono);font-size:.72rem;color:var(--faint)">${p.counts.knowledge} docs</span></div><p style="color:var(--muted);font-size:.82rem;margin:8px 0 0">Citation-grounded knowledge bank with decision trees &amp; best-practice libraries.</p></div>`).join("");

        $("#view").innerHTML = `
          <div class="page-head"><span class="eyebrow">Resources</span><h1>Templates, decision trees &amp; knowledge</h1>
            <p class="lede">${totalTemplates} templates and ${totalKnowledge} knowledge docs ship across the marketplace. Export the full documentation or jump into a plugin's knowledge bank.</p></div>

          <div class="section-title"><h2>About RavenClaude</h2><span class="hint">the marketplace at a glance</span></div>
          <div class="stats">
            <div class="card stat"><span class="v">${s.plugins}</span><span class="k">Active Plugins</span><span class="sub">in the catalog</span></div>
            <div class="card stat"><span class="v">${s.specialists}</span><span class="k">Specialists</span><span class="sub">agents on the roster</span></div>
            <div class="card stat"><span class="v">${s.hooks}</span><span class="k">Active Hooks</span><span class="sub">gates &amp; guardrails</span></div>
            <div class="card stat"><span class="v">${s.skills}</span><span class="k">Skills</span><span class="sub">invokable capabilities</span></div>
            <div class="card stat"><span class="v">${s.scenarios || 0}</span><span class="k">Scenarios</span><span class="sub">real-engagement field notes</span></div>
            <div class="card stat"><span class="v">${s.tools || 0}</span><span class="k">Runnable tools</span><span class="sub">stdlib calculators &amp; checkers</span></div>
          </div>

          <div class="grid cols-3" style="margin-bottom:8px">
            <a class="card" href="README.md" style="display:block"><div class="action-tile"><span class="ico">${svg("info")}</span><span><span class="t">README</span><span class="d">Marketplace overview &amp; setup</span></span></div></a>
            <a class="card" href="#/observe" style="display:block"><div class="action-tile"><span class="ico">${svg("sliders")}</span><span><span class="t">Deep Dashboard</span><span class="d">Full posture &amp; tribunal controls</span></span></div></a>
            <a class="card" href="CHANGELOG.md" style="display:block"><div class="action-tile"><span class="ico">${svg("git")}</span><span><span class="t">Changelog</span><span class="d">Version history</span></span></div></a>
          </div>

          <div class="section-title"><h2>How the marketplace works</h2><span class="hint">architecture</span></div>
          <div class="grid cols-2">
            <div class="card"><b>The marketplace model</b><p style="color:var(--muted);font-size:.85rem;margin:8px 0 0">A private "app store" for Claude Code. The product is the set of plugins in <code>plugins/</code>. To use one, run <code>/plugin install &lt;name&gt;@ravenclaude</code> inside any project and that plugin joins your session — its <code>CLAUDE.md</code> auto-loads when active.</p></div>
            <div class="card"><b>Hierarchical dispatch</b><p style="color:var(--muted);font-size:.85rem;margin:8px 0 0">The top-level session is the <b>Team Lead</b>; it dispatches specialists (specialists never spawn specialists — enforced by <code>guard-recursive-spawn</code>). Every specialist ends its report with a <code>---RESULT_START---…---RESULT_END---</code> JSON block (Structured Output Protocol) the Team Lead parses to route.</p></div>
            <div class="card"><b>Plugin separation</b><p style="color:var(--muted);font-size:.85rem;margin:8px 0 0"><code>ravenclaude-core</code> stays domain-neutral — generic agents, dispatch playbook, gates, hooks. Domain plugins extend core via skills + knowledge, not parallel agents.</p></div>
            <div class="card"><b>Layout &amp; CI gates</b><p style="color:var(--muted);font-size:.85rem;margin:8px 0 0">Every new file's path must match a glob in <code>.repo-layout.json</code> (the <code>enforce-layout</code> hook + <code>validate-layout</code> CI). Each CI gate proves bidirectionally that it fails on a known-bad input and passes on a known-good one (<code>scripts/audit-gates.sh</code>).</p></div>
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
          <div class="callout">${svg("download")}<span>Regenerate this portal from source: <code>python3 scripts/generate-index-dashboard.py</code>. It reads the live catalog so the docs never drift.</span></div>`;
      }

      /* ---------------- Served-mode (native merge) ----------------
         The dashboard sub-app is folded into THIS document and carries its
         own served-vs-static detection (its /__* per-card fetches fall back
         to empty states when the local server isn't running). The shell no
         longer probes or renders an iframe banner — there is no iframe. */

      /* ---------------- ⌘K Command Palette ----------------
         Categorized search across plugins, specialists, skills, hooks,
         and a set of "Quick action" commands. Built once at init from D.
         Keyboard nav: arrows + enter, esc closes, tab cycles within modal. */
      function buildPaletteIndex() {
        const idx = [];
        // Quick actions — top-priority category, always present
        const QA = [
          { kind: "action", label: "Apply Strict Production posture", meta: "Configuration", hay: "apply strict production posture", route: "#/configure", preset: "strict_production" },
          { kind: "action", label: "Apply Client Delivery posture (recommended)", meta: "Configuration", hay: "apply client delivery posture recommended", route: "#/configure", preset: "client_delivery" },
          { kind: "action", label: "Apply Exploratory posture", meta: "Configuration", hay: "apply exploratory posture", route: "#/configure", preset: "exploratory" },
          { kind: "action", label: "Apply Maximum Autonomy posture", meta: "Configuration", hay: "apply maximum autonomy posture", route: "#/configure", preset: "maximum_autonomy" },
          { kind: "action", label: "Open posture editor", meta: "Configuration", hay: "open posture editor configuration", route: "#/configure" },
          { kind: "action", label: "Open deep dashboard", meta: "rc dashboard", hay: "open deep dashboard server rc", action: "copyCmd", cmd: "rc dashboard" },
          { kind: "action", label: "Toggle dark mode", meta: "Theme", hay: "toggle dark mode theme", action: "toggleTheme" },
          { kind: "action", label: "Show onboarding checklist", meta: "Onboarding", hay: "show onboarding checklist setup", action: "showOnboarding" },
          { kind: "action", label: "Browse by use case", meta: "Marketplace", hay: "browse use case i want to intent lookup", route: "#/discover" },
        ];
        QA.forEach((q) => idx.push(q));
        // Plugins
        D.plugins.forEach((p) => {
          idx.push({ kind: "plugin", label: p.label, meta: p.category_label, hay: (p.label + " " + p.description + " " + p.keywords.join(" ")).toLowerCase(), route: "#/discover/" + p.category, open: p.name });
          // Copy-install action per plugin
          idx.push({ kind: "action", label: `Copy install command for ${p.label}`, meta: "Install", hay: `copy install ${p.name} ${p.label}`.toLowerCase(), action: "copyCmd", cmd: `/plugin install ${p.name}@ravenclaude` });
        });
        // Specialists
        D.plugins.forEach((p) => p.agents.forEach((a) => idx.push({ kind: "specialist", label: a.label, meta: p.label, hay: (a.label + " " + (a.description || "") + " " + p.label).toLowerCase(), route: "#/team" })));
        // Skills (new — from §G scanner)
        D.plugins.forEach((p) => (p.skills_index || []).forEach((s) => idx.push({ kind: "skill", label: s.label, meta: p.label, hay: (s.label + " " + (s.description || "") + " " + p.label).toLowerCase(), route: "#/discover/" + p.category, open: p.name })));
        // Hooks (new — from §G scanner)
        D.plugins.forEach((p) => (p.hooks_index || []).forEach((h) => idx.push({ kind: "hook", label: h.name, meta: p.label + " · " + h.event, hay: (h.name + " " + (h.description || "") + " " + p.label).toLowerCase(), route: "#/discover/" + p.category, open: p.name })));
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
        // Render the "Recent" section first when input is empty
        if (!q) {
          let recent = [];
          try { recent = JSON.parse(localStorage.getItem("rc-palette-recent") || "[]"); } catch (e) { recent = []; }
          const recentItems = recent.map((label) => PALETTE_IDX.find((x) => x.label === label)).filter(Boolean).slice(0, 5);
          if (recentItems.length) {
            html += `<div class="palette-section"><div class="palette-section-label">Recent</div>`;
            recentItems.forEach((m) => {
              const i = paletteFlat.length;
              paletteFlat.push(m);
              const ico = svg(PALETTE_ICONS[m.kind] || "sparkle");
              html += `<div class="palette-item" data-i="${i}" role="option"><span class="pi-ico">${ico}</span><span class="pi-label">${esc(m.label)}</span><span class="pi-meta">${esc(m.meta || "")}</span></div>`;
            });
            html += `</div>`;
          }
        }
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
        // Remember this action for the palette "Recent" section
        try {
          const recent = JSON.parse(localStorage.getItem("rc-palette-recent") || "[]");
          const newRecent = [m.label, ...recent.filter((x) => x !== m.label)].slice(0, 5);
          localStorage.setItem("rc-palette-recent", JSON.stringify(newRecent));
        } catch (e) { /* localStorage may be unavailable in sandboxed previews */ }

        if (m.preset) {
          // Apply preset action — navigate to configuration; the view applies the preset on render.
          // BUG #1 fix: if already on the same hash, hashchange won't fire,
          // so route() never re-runs and the preset never applies. Call route() directly.
          window.__pendingPreset = m.preset;
          if (location.hash === m.route || (m.route === "#/configure" && location.hash === "#/configure/")) {
            route();
          } else {
            location.hash = m.route;
          }
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
      // (Dead SEARCH_IDX + gotoSearch aliases removed — no callers.)

      /* ---------------- Router ---------------- */
      // Native-merged routes (dashboard + catalog) light up the matching nav
      // item; their sub-routes are owned by the sub-app shown in #dash-root /
      // #catalog-root.
      // Map any route (canonical, legacy alias, dashboard tab, or plugin-*) to the
      // NAV section that should light up.
      function resolveNavActive(section) {
        if (SECTION_ALIAS[section]) section = SECTION_ALIAS[section];
        if (NAV.some((n) => n.id === section)) return section;
        if (DASH_OWNER[section]) return DASH_OWNER[section];
        if (section && section.startsWith("plugin-")) return "catalog";
        return "control";
      }
      function route() {
        const raw = location.hash.replace(/^#\/?/, "") || "home";
        let [section, sub] = raw.split("/");
        renderNav(resolveNavActive(section));
        // NB: the mobile nav pane is intentionally NOT closed here. Clicking a
        // top-level category should expand its subcategories in-place (pane stays
        // open); closing is handled by the sidebar click handler (a subcategory
        // leaf / a childless section / brand-footer link) and the scrim.

        // Legacy top-level alias → canonical section (marketplace→catalog, home→control,
        // and the P5 named removals #/configure/#/overview/#/simulator → control).
        if (SECTION_ALIAS[section]) section = SECTION_ALIAS[section];

        if (section && section.startsWith("plugin-") && section !== "plugin-vars") {
          // Rich per-plugin REFERENCE lives in the shell (Catalog). The CONFIGURE
          // half (editable variables) stays on the dashboard host — Marketplace
          // "Details" drives this. #/plugin-vars (the P1 picker) is EXCLUDED here —
          // it is owned by the dashboard host via DASH_OWNER["plugin-vars"], so it
          // falls to the DASH_OWNER branch → viewDashboard("plugin-vars", <plugin>).
          showHost("view");
          window.__openPlugin(section.slice(7));
          $("#view").focus({ preventScroll: true });
        } else if (section === "control") {
          // Control = posture/settings (job 1, the one write surface). Land on
          // Settings; a sub-tab (#/pipeline, #/web-access) hits DASH_OWNER below.
          viewDashboard("settings", sub);
        } else if (section === "activity") {
          // Activity = "what my agents did" (job 2). Land on the run feed.
          viewDashboard("activity", sub);
        } else if (section === "guardrails") {
          // Guardrails = "what fired" (job 3). Land on perimeter alerts (Heimdall).
          viewDashboard("heimdall", sub);
        } else if (section === "observe") {
          // Retired route → Activity's run feed (back-compat for old bookmarks).
          viewDashboard("activity");
        } else if (section === "act") {
          // Retired route → Commands (back-compat for old bookmarks).
          viewDashboard("commands");
        } else if (DASH_OWNER[section]) {
          viewDashboard(section, sub);
        } else if (section === "catalog" || section === "discover") {
          showHost("view"); viewMarketplace(sub); $("#view").focus({ preventScroll: true });
        } else if (section === "learn") {
          showHost("view"); viewResources(); $("#view").focus({ preventScroll: true });
        } else {
          // Unknown / retired top-level route → Control (job 1, the default landing).
          // P5 (dashboard-consumption): viewHome/viewConfiguration/viewTeam were deleted;
          // the shell default now agrees with the shared activate() fallback (panel-settings
          // behind Control) so both land the user on the same visible surface — never a
          // dead view or a blank host.
          viewDashboard("settings", sub);
        }
        window.scrollTo({ top: 0 });
      }
      window.addEventListener("hashchange", route);

      /* ---------------- Chrome wiring ---------------- */
      // Commerce nav scroll-blur: veil the topbar once the page scrolls past ~12px
      // (ported from the commerce site's Nav.astro is-scrolled toggle).
      const _topbar = $(".topbar");
      if (_topbar) {
        const onTopbarScroll = () => _topbar.classList.toggle("is-scrolled", window.scrollY > 12);
        onTopbarScroll();
        window.addEventListener("scroll", onTopbarScroll, { passive: true });
      }
      // Sidebar collapse (persisted)
      if (localStorage.getItem("rc-sidebar") === "collapsed") document.body.classList.add("sidebar-collapsed");
      $("#collapse-toggle").addEventListener("click", () => {
        document.body.classList.toggle("sidebar-collapsed");
        localStorage.setItem("rc-sidebar", document.body.classList.contains("sidebar-collapsed") ? "collapsed" : "open");
      });
      // Mobile nav
      $("#mobile-toggle").addEventListener("click", () => document.body.classList.toggle("mobile-nav-open"));
      $("#scrim").addEventListener("click", () => document.body.classList.remove("mobile-nav-open"));
      // Mobile drill-down: a top-level category with subcategories expands
      // in-place (pane stays open); a subcategory leaf — or a childless section /
      // brand-footer link — closes the pane.
      $("#sidebar").addEventListener("click", (e) => {
        if (!document.body.classList.contains("mobile-nav-open")) return;
        const link = e.target.closest("a");
        if (!link) return;
        if (link.classList.contains("nav-item") && navChildren(link.getAttribute("data-nav"))) return;
        document.body.classList.remove("mobile-nav-open");
      });

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

      // Re-probe served mode when the tab regains visibility/focus (E4/L4): a
      // detached server can stop or idle-expire while the tab stays open, so a
      // one-shot probe at load can go stale — this makes the failure state (and
      // the recovery) self-correcting without a manual reload.
      document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "visible") reprobeServed();
      });
      window.addEventListener("focus", reprobeServed);

      probeServed(); // resolve served/static early so the banner is flicker-free
      route();
    </script>
  </body>
</html>
"""
