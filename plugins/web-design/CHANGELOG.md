# Changelog — web-design

Versioning is semver; bump on every user-visible change and keep it in sync with the catalog entry in `.claude-plugin/marketplace.json`.

## [0.22.0] — 2026-10-27

### Added

- **`templates/block-site/`**: a starter kit, so anyone can build a block site with no private composer.
  - `tokens.css` holds the values a site tunes.
  - `layout.css` is the layout contract:
    - a page grid with `full`/`wide`/`content` lines;
    - rhythm tokens and tones;
    - intrinsic primitives;
    - a count-aware card grid for 1–6 items;
    - media frames and a copy-anchored scrim;
    - text safety;
    - dark, forced colours, more contrast, reduced motion, RTL and print.
  - `block.schema.json`, `site-manifest.schema.json`, `catalog.md` (18 canonical blocks), five exemplar block contracts, an example manifest, and `gallery.html`.
- **`scripts/block_site_check.py`** (stdlib), with `catalog`, `manifest`, `tokens` and `fixtures` commands and a `--self-test` of 43 rows.
- **`scripts/layout-probe.js`**: 18 rendered-page checks in a dependency-free browser function.
- **`scripts/device_matrix.mjs`**: runs the probe across 28 viewports, ±1px around every `@media` width, an optional sweep, and three themes. `--self-test` plants 22 defects (every check the probe has), requires a clean control over 306 states, and measures all 18 count × width cells of the card grid. A layout shift counts only when it repeats in 3 of 3 loads (the measured reason is in the knowledge file §11).
- **Knowledge:** `block-layout-system-2026.md`. The contract, its rationale and numbers, browser support from MDN browser-compat-data read 2026-10-27, the verification ladder, and ten measured pitfalls.
- **Command:** `/web-design:new-block-site`, gated step by step.

### Changed

- `block-composed-site` gains Mode 0 (start from the kit), the layout contract, a proof ladder for every mode, and four new pitfalls.
- `adaptive-layout` Step 7 points at this plugin's own device matrix instead of the owner's private factory.
- `test_web_design_checks.py` (run by CI Gate 317) gains five block-site tests.

## [0.21.0] — 2026-10-27

### Added

- **Knowledge:** `text-over-photo-contrast-2026.md`. How to measure text over a photograph, which token-pair checks cannot score:
  - find each line's boxes and clip them to their clipping ancestors;
  - resolve the colour through a canvas;
  - hide the glyphs but keep their shadow and background, and assert the hide landed;
  - capture the viewport only (a full-document capture grows every `svh` hero) and assert its geometry;
  - score each line at its 5th-percentile composited pixel against 4.5:1 or 3:1;
  - block analytics during the run;
  - prove the probe with a mutation that must fire.

  The fix is a scrim band anchored to the copy rather than the photo. Built and measured in the owner's site factory (RavenPower-website-factory PR #131), where it found the kit's own example at 1.25:1 and a hand-built template at 1.24–3.27:1. WCAG facts re-read from Understanding SC 1.4.3 on 2026-10-27.
- **`block-based-site-composition-2026.md`:**
  - §7 is the generation projection as built: what it offers a model, the facts that stand, what the inverse refuses, the round-trip proof, and what is unproven. §5 now lists every documented structured-outputs limit, including the 24-optional and 16-union caps.
  - §8 is the first measured per-site cost: $5.16 single tier and $9.74 growth tier. The visual pass is about half of each, and cache reads are 72–74%.
  - Pitfalls 17–23: the hero scrim, a stranded card, dark screenshots, a gate exemption that matched nothing, printed URLs that moved, merge regressions, and one fact written twice.

### Changed

- `block-composed-site` runs the photo-contrast probe in its visual pass. It gains a structured-outputs generation step and a budget note, and five new pitfalls.
- `adaptive-layout` Step 7 and `accessibility-review` Pass 5 point at the photo-contrast method. Text over a photo that was not measured is reported as not measured, never as passing.

## [0.20.0] — 2026-10-26

### Added

- **`skills/adaptive-layout/`** — make a site adapt to desktop, laptop, phone (both orientations), tablet, iPad windows and foldables like iPhone Duo the way Apple and WebKit prescribe: one document and feature detection (iPad sends a Mac UA; iOS 26 freezes the UA OS version), the exact viewport tag, `viewport-fit=cover` only with all four safe-area insets, `vh`-then-`svh`/`lvh`/`dvh` heights, content-driven tiers in `em` plus container queries, `max(16px, 1rem)` form text, WCAG 2.5.8 targets, 2x-capped art direction, optional Viewport Segments enhancement, and a device matrix with ±1px breakpoint boundaries as the proof.
- **Knowledge:** `apple-adaptive-web-2026.md` — HIG and WebKit guidance with sources (the HIG's device table is gone since 2026-09-09; Safari 26 tints its bars from the page background and edge-fixed elements; every Home Screen site opens as a web app in iOS 26; `rem` ignores iOS Dynamic Type; no `prefers-reduced-transparency` in Safari), apple.com measured at 35 viewports (734/1068 tiers, 833/834 nav, height-aware hero, 2x-capped art direction), the iPhone Duo viewport table from WebKit's Safari 27.1 post (iPhone Duo shipped 2026-10-23, verified against the Apple Newsroom release), Viewport Segments and Device Posture support, multitasking widths and a device test matrix. Retrieved 2026-10-26.

### Changed

- `frontend-implementer`, `visual-designer` and `accessibility-auditor` carry a pointer to `adaptive-layout`; `static-site-implementation` links it for device adaptation; `templates/launch-checklist.md` gains device-matrix, viewport-tag, viewport-unit and real-Safari items.

## [0.19.0] — 2026-10-26

### Added

- **`skills/interface-craft/`** — raise a surface to the craft bar of Apple, Stripe, Cloudflare, Starlink, Tesla and recent game menus: choose a register per surface, apply its sourced moves with their guardrails, verify on the rendered page in both themes at 390 and 1440 px.
- **`skills/block-composed-site/`** — build many customer sites from a catalog of section blocks selected by purchased features; the agent writes a typed manifest, never markup. Block contract, feature and tier mapping, resolver rules, must-fail gates, drift detection, upgrade rollout, and the pitfalls measured while building the owner's factory block system (RavenPower-website-factory PR #118).
- **`skills/form-builder/`** — build or upgrade a tool owners use to create their own forms: typed definition model, draft + immutable versions keyed by stable field ids, typed condition trees run by one allow-listed interpreter on client and server, save-time logic checks, a phased field catalog, inbox/CSV/webhooks/CRM, server-recomputed payments.
- **`skills/visual-builder/`** — make any builder (form, contact card, Wallet pass, page) appealing and easy: same-code preview, click-to-insert with drag as a bonus, menu moves, two disclosure levels, undo as patches, autosave with conflict checks, publish with blast radius, constraint-aware warnings.
- **Knowledge:** `form-builder-2026.md` and `visual-builder-ux-2026.md` (retrieved 2026-10-26; measured drag-and-drop bundle sizes).
- **Knowledge:** `interface-craft-reference-brands-2026.md` (Apple, Stripe, Cloudflare, Starlink, SpaceX, Tesla — read from live production CSS/HTML and primary sources), `interface-craft-fundamentals-2026.md` (motion, colour, type, layout, states, process, with sourced numbers), `game-ui-lessons-for-the-web-2026.md` (game menu and HUD craft translated to 2026 web platform features, and what must not be copied), `block-based-site-composition-2026.md` (prior-art data models, architecture, gates, distribution, AI-agent practices, pitfalls). All dated 2026-10-26 with OBS/INF/`[unverified]` labels.

### Changed

- `visual-designer`, `ux-designer`, `frontend-implementer` and `web-architect` carry a short pointer paragraph to the new skills and knowledge.
- `visual-designer`'s motion opinion no longer asserts ease-in for exits as settled: it names the Material 2 vs Emil Kowalski conflict and states this plugin's default (ease-out both ways, exits ~20% shorter).

## [0.18.6] — 2026-10-20

### Fixed (2026-10-20 autonomous repo review, PR #1389)

- A-24 flesch_kincaid check fails closed on unscorable text
- A-23 say strict mode feeds findings back, not that it blocks
- A-25 colour check exempts token files by basename, sees 4/8-digit hex

## [0.18.5] — 2026-10-13

### Added

- **`best-practices/ogp-metadata-every-shareable-page.md` § Messages (iMessage) — Apple TN3156.** Apple's own rules for rich link previews, quoted from TN3156 (fetched 2026-10-13): no text in the preview image (Messages draws `og:title` in its caption under the image), a short `og:title` with no site branding (`og:site_name` carries it), metadata in the served HTML (no JS, no meta refresh), the same metadata for every user agent (Messages' measured UA), the 900 px / 150 px / 108 px / 1 MB / 10 MB limits, 1200 × 630 being enough (an Apple engineer's forum answer; "2400 × 1256" is folklore), aspect ratio being undocumented (keep a portrait subject centre-crop-safe), previews built on the sender's device and frozen once sent, and image URLs that must return image bytes. Plus the per-entity image pattern (pixels from visual fields only, text in `og:title`) and a device-test step for validation.

### Changed

- **The OGP image spec no longer says "no tiny text"; it says keep words out of the image** for Messages, and the example `og:title` no longer appends the site name.

## [0.18.3] — 2026-09-15

### Fixed

- **`web-anti-patterns-exit-code-guidance`** — `hooks/check-web-anti-patterns.sh`'s comment and runtime
  banner told a maintainer to change `exit 0` to `exit 1` to BLOCK on a violation, but Claude Code's
  PreToolUse contract only blocks on `exit 2` (`exit 1` is a non-blocking error it silently swallows),
  so following it gave false enforcement. Now documents and implements the sibling convention: set
  `WEB_DESIGN_STRICT=1` to block via `exit 2`.

## [0.16.3] — 2026-09-01

### Added

- **`knowledge/design-md-token-interop.md`** — verified this repo's `design-tokens-scaffolding` W3C DTCG pipeline against `google-labs-code/design.md` (Google Labs' alpha-stage `DESIGN.md` spec for handing design tokens + visual-identity rationale to a coding agent in one file). Same token vocabulary (DTCG), different delivery envelope: an optional, opt-in export at the `brand-identity-studio` `assemble-brand-book` handoff, never a pipeline change. Cross-linked from the knowledge bank (`CLAUDE.md` §8a) and `design-tokens-scaffolding/SKILL.md` §5. Prompted by a review of [generativeprogrammer.com's survey of emerging agent-facing markdown formats](https://generativeprogrammer.com/p/emerging-markdown-formats-that-shape) — most of the formats it describes (`AGENTS.md`, `CLAUDE.md`, `SKILL.md`, `MEMORY.md`) this marketplace already implements; `DESIGN.md` was the one genuinely new, verified, actionable gap.

## [0.16.2] — 2026-08-17

### Fixed

- **`conversion-design` was shipping folklore as a benchmark.** §3 stated "each additional required field reduces completion by ~5–7%" and carried a *"Sign-up form field benchmarks (2026, self-serve SaaS)"* table mapping field count to completion ranges (1 field → 35–50%, 7+ → <10%). Both were **unsourced**, and both are contradicted by the evidence: a documented A/B test where **removing fields dropped conversion 14%** while merely **relabelling the same fields raised it 19.21%**, plus a 30+ question form converting at **53%** — the source's own verdict on "is shorter better?" being *"No, not necessarily"* ([ventureharbour.com](https://ventureharbour.com/how-form-length-impacts-conversion-rates/), retrieved 2026-08-17, summarising a ConversionXL / Michael Aagaard case).

  Removed rather than re-cited: the figures usually quoted in support are single-company tests, not controlled research, and calling them "benchmarks" lent invented precision the underlying data does not carry.

  The **design discipline is unchanged and now rests on an argument that holds** — cut a field you cannot name a *use* for, on data-minimisation grounds (less to store, less to breach, less to justify at privacy review), and do not promise a conversion lift for it. If conversion is the goal, test it; field count is worth A/B-testing precisely *because* its effect is not predictable in advance. The hygiene checklist already argued from justification ("the minimum that fulfills the action") and needed no change.

  Found by a cross-source conflict during a `/forge` run: the shipped skill (claims-table row 3) contradicted primary-source research (row 90). Swept the rest of `plugins/` for the same claim class — **no other instance**.

## [0.16.1] — 2026-08-14

### Changed

- Dropped hand-maintained artifact-count literals from the plugin description (D1). The roster enumerates itself; Gate 206 forbids the digit.

## [0.16.0] — 2026-08-13

### Added

- **Design-schema mimicry priors** on `visual-designer` + `frontend-implementer` (body-only; no frontmatter change). Each agent gains a `## Design-schema mimicry` section in the exact slot/style of the existing `## Visual feedback loop` prior, pointing at the new `ravenclaude-core/skills/design-clone` skill: **clone the craft, swap the identity**, with the browser-gated-fidelity boundary stated up front (offline structural diff = a "declares the same design system" sanity check; the `ssim_score` render-compare gate is the fidelity verifier, present only with a browser tool). A cross-plugin row was added to the §8a knowledge-bank table.

## [0.15.0] — 2026-07-21

### Added

- **Dual-analytics standing standard (`dual-analytics-standard`).** `CLAUDE.md` §3 house-rule #11 gains a **bounded, standing exception**: the **GA4 (Consent Mode v2) + Cloudflare Web Analytics** house pair ships together as ONE "house analytics" inventory line in every new site, wired placeholder-until-provisioned (empty ⇒ inert, zero network), each independently PROD + valid-id guarded. A named exception, **not** a repeal — a third analytics tool is still forbidden. The full reference implementation — the snippet, the `isRealGaId`/`isRealCfToken` validators (which reject dummy shapes like `G-XXXXXXXXXX`), the per-stack PROD gates, the authed/internal-surface default (analytics never auto-fires on a logged-in/internal surface), the honest CSP/SRI story, the EU + data-quality caveats, and the measured CWV budget — is added as `skills/third-party-script-hygiene` **§8–9**. `gold-standard-website-pipeline` G5/G7 + `templates/launch-checklist.md` wire it in (G7 **measures** the pair against a `<50 ms` TBT budget, never blanket-passes it).

### Changed

- `third-party-script-hygiene` category-budget table: Analytics **`1 → 2 (bundled house default)`**; both the budget row and the "two analytics tools to compare data" anti-pattern now carry the sanctioned-pair carve-out (so the pipeline's own hygiene gate accepts the two beacons).

## [0.14.3] — 2026-07-09

### Changed

- **Pseudonymized a private client codename** in `knowledge/gold-standard-website-references-2026.md` — a cross-link that referenced a research directory named after the codename now points at its renamed (`contoso`) path. Neutral placeholder; no consumer-facing behavior change.

## [0.14.2] — 2026-07-08

Weekly Tier-A news sweep (2026-07-08) — **addition** in `knowledge/modern-web-stacks-2026.md`: Astro shipped a new major (**7.x**); the stack note now reads **Astro 7+** (the islands / zero-JS / Content-Layer / Server-Islands model carries forward). Re-verified via the withastro/astro GitHub releases. **Migration:** none — knowledge-file content only.

## [0.14.0] — 2026-07-06

The **gold-standard website pipeline** — a gated, fail-closed checklist the Team Lead runs for _every_ new website so quality is designed in, not bolted on — plus the two plugin gaps that pipeline surfaced, closed in the same release. Skills 11 → 13; commands 5 → 6.

### Added

- **`skills/gold-standard-website-pipeline/` (the marquee addition).** A nine-gate, fail-closed orchestration pipeline (discovery → IA → design/tokens → content → build → accessibility → performance → SEO/AEO → pre-launch sign-off) that the Team Lead drives for any new **marketing site / web app / ecommerce** build. Each gate states entry · dispatch (the real owning agent → skill) · **checkable, standards-anchored acceptance criteria** (WCAG 2.2 AA, Core Web Vitals @p75, security headers, consent mechanics — every bar a number or a pointable artifact) · fail-closed outcome · typed artifact. Includes a **site-type adaptivity matrix**, a **dependency DAG** (G3 ∥ G4; G6 ∥ G7 ∥ G8b — real parallelism, not a flat list), a shared P0–P3 severity/owner/date vocabulary, seams that **defer-don't-duplicate** (app build → `frontend-engineering`, growth economics → `ecommerce-dtc`, any auth/payments/PII surface → `ravenclaude-core/security-reviewer`, mandatory at G9), and a **lab-vs-field CWV split** (G7a Lighthouse+budget+RUM pre-launch; G7b field data as a post-launch G9 Condition) plus **tiered evidence ladders** so a browser-tool-less agent closes _Conditional_, never wedged. Terminates in one **🟢 Go / 🟡 Conditional / 🔴 No-go**. Research-grounded (see the new reference doc) and adversarially reviewed to gold standard.
- **`commands/new-website.md`** — the thin `/web-design:new-website` entry that loads and drives the pipeline.
- **`skills/static-site-implementation/`** — the generic **non-React static build skill** (semantic HTML + token-driven CSS, SSG-first Astro/11ty/Hugo/plain HTML+CSS, islands only where earned; reflow-to-320px, in-markup performance, accessible markup). Closes the coverage gap the pipeline surfaced at G5: the primary marketing archetype's static-first default previously had no dedicated build skill (only the Fluent-UI-v9-only `fluent-react-implementation`). G5's non-React static path now dispatches it directly.
- **`knowledge/gold-standard-website-references-2026.md`** — the curated exemplar set the pipeline distills: **10 gold-standard websites** (marketing / web-app / ecommerce), each mapped to the gate its lesson informs, and **10 gold-standard agentic website-building tools/plugins**, each mapped to the pipeline-craft idiom it teaches. Unverifiable claims flagged; `Last reviewed: 2026-07-06`.
- **`scripts/flesch_kincaid.py`** — a stdlib-only Flesch-Kincaid Grade Level checker (`grade` / `check --max`), so G4's reading-level bar is a runnable Tier-1 check (the "checker over restated rule" discipline), alongside the existing `contrast_ratio.py`.

### Changed

- **`security-reviewer` routing is now uniform across all 7 agents.** `accessibility-auditor`, `content-strategist`, `performance-engineer`, `ux-designer`, and `visual-designer` each gained an archetype-appropriate `security-reviewer` escalation row (previously only `web-architect` + `frontend-implementer` named it), so the pipeline's zero-exception G9 security gate is true per-agent as well as pipeline-side.
- **`CLAUDE.md` "Adjacent plugins" seam** now names the **`ecommerce-dtc`** reciprocal boundary (storefront build here; commerce whether/what there) and the uniform `security-reviewer` routing — closing two of the three coverage gaps the pipeline's honest §9 self-grade identified (the third, the static-build skill, is closed by `static-site-implementation` above).
- **Templates brought into gate-contract alignment with the pipeline** (so an agent driving a template verbatim can actually satisfy its gate): `design-brief.md` gained the G1 block (archetype, stack + ≥2 alternatives, numeric per-template perf budget, success-metric + measurement, escalation flags); `launch-checklist.md` gained a mandatory **Security review (`security-reviewer`)** section (HSTS/CSP/COOP-CORP-COEP headers + a no-waiver sign-off line) and the five falsifiable consent sub-checks, plus sign-off lines on Analytics / Legal / Communication; `site-architecture.md` made the content model unconditional and added a redirect-plan table; `content-style-guide.md` gained the G4 content-ledger scaffolds (≥5-state screen inventory, trust-signal placement, FK ceiling, KKCR matrix); `accessibility-audit-report.md` gained the G6 evidence-tier (A/B) declaration + the 9-SC WCAG 2.2 checklist.

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
