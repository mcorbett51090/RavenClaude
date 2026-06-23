# Changelog — web-design

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.13.0] — 2026-06-09

Version bump previously unlogged here (rolls up `0.12.0` → `0.13.0`); the change that set `0.13.0`:

- feat: visual-feedback-loop — render→see→iterate for web + reporting agents (#378)

## [0.12.0] — 2026-06-05

Value-add build-out — adding the net-new gap left after PR #315 (which added the consolidated `web-design-decision-trees.md`, the best-practices bank, and the templates): the scenarios bank, the technical-runtime tier (LSP + a runnable contrast checker), and two complementary decision trees. Every value-add menu item is dispositioned (built or recorded N-A with reason); see [`CLAUDE.md`](CLAUDE.md) §14 "Value-add completeness (build-out 2026-06-05)".

### Added

- **scenarios/ bank (4 field notes).** `wcag-contrast-and-focus-order-audit` (Lighthouse 100 ≠ accessible; measure contrast against the real rendered background + every state; fix focus order in the DOM, never with positive `tabindex`) — the pre-existing stray partial, reconciled and kept; `lcp-perf-budget-hero-image` (for LCP, fix discovery + priority before size — server-render the hero, preload, `fetchpriority=high`, never lazy-load it); `design-token-drift-hardcoded-hex` (tokens are a primitive→semantic indirection layer, not a color file — dark mode is the test that proves you have one; gate hardcoded hex in CI); `cls-layout-shift-and-seo-meta-regression` (diagnose CLS by source; treat per-page metadata + indexability as a launch gate). Matches the existing `scenarios/README.md` index and the 9-field schema.
- **Decision-tree knowledge (NEW, complementary).** `knowledge/css-architecture-and-a11y-remediation-decision-trees.md` — two Mermaid trees: **CSS architecture / styling-approach selection** (RSC-aware, zero-runtime default: Tailwind v4 `@theme` vs CSS Modules / modern CSS vs zero-runtime vs runtime CSS-in-JS) and **accessibility-remediation prioritization** (P0 launch-blocker → P1 fast-follow → P2 dated-backlog → P3 enhancement, ranked by user impact not tool count). Chosen to **complement** PR #315's 13-tree `web-design-decision-trees.md`, not duplicate it.
- **Runnable tooling.** `scripts/contrast_ratio.py` (stdlib only, Python 3.8+) — `pair` (one foreground/background vs. WCAG SC 1.4.3 + SC 1.4.11 thresholds for normal/large text + UI components) and `check` (batch-assert token/usage pairings stay in contrast — the token-drift guard). A checker, not a renderer: you supply the actual displayed colors. Closes the dangling reference the contrast scenario already pointed at.
- **`.lsp.json`** (CSS / HTML / ESLint language servers) wired via `plugin.json` `lspServers` — markup/style-centric code intelligence for a domain that ships real HTML/CSS/JS.
- **CLAUDE.md** §8b (scenarios bank & runnable tooling, replacing the old §8b TODO), §12 (LSP tier), §13 (recommended-not-bundle MCP, incl. Figma Dev Mode MCP), §14 (value-add disposition table), §15 (milestones); knowledge-bank table (§8a) updated with the two decision-tree files.

### Decisions (recorded, not built)

- **No bundled MCP server.** The most-useful design-tool server — Figma's official **Dev Mode MCP server** — is first-party from the vendor, per-account-authenticated, metered (free in beta, slated to become usage-based paid), and write-capable (writes components/variables/auto-layout back to the canvas); the two browser servers (Google `chrome-devtools-mcp`, Microsoft `@playwright/mcp`) are first-party + browser-driving. The bundling doctrine routes all three to **recommend, don't bundle** with a `security-reviewer` gate. Documented the recommended `claude mcp add …` / desktop-enable paths instead. No invented servers (the community `GLips/Figma-Context-MCP` exists but is not first-party and is not recommended over Figma's own server).
- **No output-style for a design-review format.** Considered and declined — the §6 Output Contract + the `accessibility-audit-report` / `seo-audit-report` templates already fix the deliverable shape; an output-style would duplicate them.
- **No `bin/`, monitors, themes, settings tuning, or new agent** — none cleared the "groundable + broadly valuable, doesn't duplicate an existing surface" bar. The perf/CWV checker stays in `frontend-engineering/scripts/perf_budget.py` (the CWV scenarios cross-reference it) rather than being duplicated here.

### Verify-at-use

- LSP support landed in Claude Code 2.0.74; the `vscode-langservers-extracted` package provides all three CSS/HTML/ESLint servers (community-maintained, active forks — vet at adoption). WCAG version (2.2 AA floor) + the contrast thresholds (4.5:1 normal / 3:1 large + UI per SC 1.4.3 / 1.4.11). Core Web Vitals "good" thresholds (LCP < 2.5s / INP < 200ms / CLS < 0.1 at the 75th pct; confirmed unchanged for 2026, INP the most-failed). Figma Dev Mode MCP server status (beta → usage-based paid), variants (desktop + remote/hosted), and write-capability; `chrome-devtools-mcp` / `@playwright/mcp` package names, tool surfaces, versions, and `chrome-devtools-mcp`'s telemetry-on-by-default. Style Dictionary v4 DTCG support + the Design Tokens Format Module reaching first stable (2025.10, 2025-10-28). All version-volatile — re-confirm against the vendor before quoting.

### Sources (retrieved 2026-06-05)

- WCAG contrast formula + thresholds — https://www.w3.org/TR/WCAG20-TECHS/G18.html , https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html , https://www.w3.org/TR/WCAG22/
- Core Web Vitals — https://web.dev/articles/vitals , https://web.dev/articles/defining-core-web-vitals-thresholds
- Figma Dev Mode MCP server — https://www.figma.com/blog/introducing-figma-mcp-server/ , https://developers.figma.com/docs/figma-mcp-server/
- Design tokens — https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/ , https://v4.styledictionary.com/reference/utils/dtcg/
- MCP bundling doctrine — [`docs/best-practices/bundled-mcp-servers.md`](../../docs/best-practices/bundled-mcp-servers.md)
