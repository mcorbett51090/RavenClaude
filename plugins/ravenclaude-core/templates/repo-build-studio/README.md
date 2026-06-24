# repo-build-studio — starter templates

Two **self-contained** pages for the [`repo-build-studio`](../../skills/repo-build-studio/SKILL.md)
loop — no build step, CDN deps only, open by double-clicking, preview from any branch via GitHub Pages
or `raw.githack.com`:

- **`marketing-page.html`** — an on-brand dark landing page (hero · capabilities · work · CTA).
- **`dashboard.html`** — a static reporting dashboard (Chart.js from a CDN, **SRI-pinned**, over inline
  sample data; KPI row + bar + doughnut).

## How to use
1. Copy one into your repo (e.g. `site/index.html` or `dashboard/index.html`).
2. In **Claude Code on the web**, prompt with the load-bearing constraint:
   > "Update this as a **single self-contained HTML file — no build step, CDN deps only, inline
   > styles** — so it renders by double-clicking. Put my real copy/colors/data in."
3. Let Claude push to a `studio/<slug>` branch → preview the branch (Pages / `raw.githack.com/<owner>/<repo>/<branch>/<path>`) → iterate → PR.

## The two rules that make this safe + portable
- **No build step → no `npm install` → no dependency lifecycle-hook code execution** (the 2025–26
  supply-chain vector). Keep it self-contained until you genuinely need a framework.
- **Inline data, or fetch from a PUBLIC read-only URL.** A dashboard needing a **private** DB/API +
  credentials is the **Tier-1** case (see the skill) — not a self-contained page.

Pin any new CDN `<script>` with `integrity="sha384-…" crossorigin="anonymous"` (compute via
`curl -sSL <url> | openssl dgst -sha384 -binary | openssl base64 -A`).
