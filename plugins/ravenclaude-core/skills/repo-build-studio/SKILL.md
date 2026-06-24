---
name: repo-build-studio
description: Build a website or dashboard by prompting Claude and watching it render live, then commit it back — by COMPOSING existing surfaces (Claude Code on the web + a self-contained-HTML constraint + a GitHub Pages/githack branch preview + a PR), not by building a custom backend. Use when someone wants the "pick a repo, prompt, see it build, ship it" loop. Covers the static/self-contained case fully; says when a real data-connected dashboard needs the heavier Tier-1 path.
allowed-tools: Read, Write, Edit, Bash, WebFetch
---

# repo-build-studio — the "prompt → watch it render → commit back" loop, composed

> **What this is.** The cheap, secure way to get the Claude-Design-style experience (prompt Claude,
> watch a website/dashboard render before your eyes, commit it to a real repo) **without building a
> custom studio backend.** It composes surfaces that already exist. FORGE verdict (2026-06-24,
> `docs/plans/2026-06-24-repo-build-studio/`): the from-scratch studio's signature feature is a
> self-canceling design and a supply-chain trap; this loop delivers the same outcome at ~0 build cost.

## The loop (the Willison pattern)

1. Open **Claude Code on the web** (`claude.ai/code`) and connect the target GitHub repo. (It clones
   into an Anthropic-managed sandbox — so any `npm install` runs **off your machine**, which is the
   whole security point; see "Why self-contained" below.)
2. **Prompt with the self-contained-HTML constraint** (the load-bearing instruction):
   > "Build/update `<page>` as a **single self-contained HTML file** — vanilla JS, **no build step**,
   > any dependencies from a CDN (`<script src>`), inline `<style>`. It must open and render correctly
   > by double-clicking the file. Put it at `<path>`."
3. Let Claude push to a **`studio/<slug>` branch** (never `main`).
4. **Preview the branch live** (pick one — all render the branch's HTML as a real page):
   - **GitHub Pages from the branch** (Settings → Pages → source = that branch) → `https://<user>.github.io/<repo>/<path>` — best for an ongoing site.
   - **`raw.githack.com`** (zero config, public repo): `https://raw.githack.com/<owner>/<repo>/<branch>/<path>` — instant, good for a quick look. *(htmlpreview.github.io is the same idea.)*
   - **Artifacts** (in the Claude Code session, Team/Enterprise) — the closest to "live repaint as it builds," for self-contained pages.
5. Iterate: prompt → Claude pushes → the preview updates (refresh, or live with Artifacts). When happy,
   **open a PR** (the `mcp__github__create_pull_request` path) to merge `studio/<slug>` → `main`.

The page IS the surface (the rendered preview); you never touch an editor. Commits land on a branch and
ship via PR — connected to GitHub on the backend, exactly as asked.

## Why "self-contained, no build step" is doing double duty

It's not just simplicity — it's the **security win**. A page with **no build step never runs
`npm install`**, so it never executes a dependency's `preinstall`/`postinstall` lifecycle hooks — the
dominant 2025–26 supply-chain attack vector (Shai-Hulud, the Mastra takeover). Combined with Claude
Code web running the work in Anthropic's sandbox (off your machine), the static path has **no
arbitrary-code-execution surface on your own credentials.** Reach for a build step (and the Tier-1 path
below) only when you genuinely must.

## Two cases — know which you're in

| You're building… | Path |
|---|---|
| A **website / marketing page / static or self-contained dashboard** (charts from a CDN lib over inline or fetched-from-a-public-URL data) | **This loop.** Fully covered. Start from [`templates/repo-build-studio/`](../../templates/repo-build-studio/). |
| A **data-connected dashboard** that needs a live DB/API + credentials to show real data | This loop renders the *chrome* but not the data plane. That's the **Tier-1** case — a thin, personal, same-origin backend studio (ephemeral egress-restricted container, `--ignore-scripts`, scoped token, secret-scan gate). **Build it only on demonstrated need**, threat-model doc first. Route the data plane to the `data-platform` plugin. See the FORGE plan. |

## Starter templates

[`templates/repo-build-studio/`](../../templates/repo-build-studio/) ships two **self-contained**
scaffolds (CDN deps, no build, double-click-to-open) that double as the live-preview demo:
- `marketing-page.html` — an on-brand landing page (hero + sections + CTA).
- `dashboard.html` — a static reporting dashboard (a CDN charting lib over inline/sample data).

Drop one into a repo, point Claude at it with the constraint above, and iterate.

## Honest limits
- **In-place HMR ("repaint without refresh") is not generically buildable** — that's the trap the
  FORGE critic found (a same-origin-AND-sandboxed iframe can escape its sandbox; HMR-through-a-proxy is
  per-framework fragile). The branch-preview refresh (or Artifacts) is the reliable substitute.
- This composes existing Anthropic/GitHub surfaces; it is **not** a product. Don't wrap it in a
  "looks like Claude Code" skin (Anthropic branding terms) — "Powered by Claude" only.

## Cross-references
- FORGE plan + the premise analysis: [`../../../../docs/plans/2026-06-24-repo-build-studio/plan.md`](../../../../docs/plans/2026-06-24-repo-build-studio/plan.md).
- Brand a generated page to a target site: the [`brand-extraction`](../brand-extraction/SKILL.md) skill.
- Iterate a page toward pixel-perfect: the [`visual-feedback-loop`](../visual-feedback-loop/SKILL.md) skill.
- Data-connected dashboards: the `data-platform` plugin (`dashboard-builder`, connectors).
