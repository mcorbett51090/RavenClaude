# FORGE plan — pixel-perfect reporting (Deneb / Vega-Lite / SVG, cross-surface)

**Slug:** pixel-perfect-reporting · **Depth:** quick · **Date:** 2026-06-09
**Panels:** A=Opus, B=Sonnet (both verified repo state independently; **converged on EXTEND, not a new plugin**).
**Owner directive (Matt, 2026-06-09, overrides the home fork):** *"I want the Deneb/Vega-Lite/SVG available for **any** agent designing reporting or visualization **anywhere** — including but not limited to web and Power BI."* → **domain-neutral home (`ravenclaude-core`)**, reachable by every viz agent.

## Decision (G6 synthesis)

**EXTEND, neutral home.** Both panels converged: do **not** create a new plugin (it re-creates the dispatch ambiguity the house rule exists to prevent, and the capability already has homes). The owner directive resolves the remaining A/B split (Panel A leaned core-for-linters; Panel B leaned power-platform): put the **cross-surface Deneb/Vega-Lite/SVG-grammar capability in `ravenclaude-core`** (domain-neutral), with **thin conditional priors on every viz-output agent across plugins**. The one inherently Power-BI-specific piece — **SVG-in-DAX** (DAX is a PBI/AS construct) — stays a `power-platform` knowledge pointer that the neutral skill links to.

**Both panels independently surfaced two repo facts that reshape scope:**
1. The in-flight **`data-viz-designer` phases 2–7 are NOT built** (only the `pbir-layout-engine` + `visual-feedback-loop` runnables exist). → coordinate; this build composes with it, doesn't override it.
2. **`power-platform` already ships the Deneb/Vega-Lite/SVG *decision* knowledge** (`power-bi-custom-visuals-toolkit.md`) + a `report-visualization-design` skill (Buhler-mold, `grid.py`). → the net-new gap is **spec-authoring + a runnable security/quality linter + a reviewer**, generalized cross-surface — NOT introducing the concepts.

## What "pixel-perfect outside Power BI" actually needs (the two capabilities)

- **(A) Pixel-perfect VISUALS — net-new, where Buhler leads, RavenClaude has nothing:** Deneb/Vega-Lite (declarative grammar) + SVG. Make these **cross-surface** (web: vega-embed / react-vega / Evidence / Observable; Power BI: Deneb; SVG: universal + SVG-in-DAX).
- **(B) Pixel-perfect LAYOUT — deepen what RavenClaude already leads:** `pbir-layout-engine` (coordinate linter) + `visual-feedback-loop` (render→see→iterate) + the design-first / grid discipline. Already strong; extend, don't rebuild.

## Phased build (for Ultraplan)

**Phase 0 — pre-build hygiene.** Confirm data-viz-designer phases 2–7 absent; reserve Gate **101** (next free after 100); re-count ravenclaude-core skills (40 after `/scout` lands → 41 after this); layout globs already permit `plugins/*/skills/**` + `knowledge/**` (no `.repo-layout.json` change). DoD: pre-build gate log.

**Phase 1 — neutral knowledge canon (`ravenclaude-core`).** `knowledge/declarative-visualization.md` — the cross-surface Deneb/Vega-Lite/SVG canon: when to use which, the grammar essentials, the **surface→delivery map** (web vega-embed/react-vega/Evidence/Observable · Power BI Deneb · Tableau extension/SVG-export · SVG-in-DAX → links to a `power-platform/knowledge/svg-in-dax-patterns.md`), the security model (Vega `loader` + `transform.lookup` external-URL vectors; SVG `<script>`/event-handler vectors), and the `visual-feedback-loop` integration (render-screenshot is the primary verification for a spec the coordinate linter can't see). Every third-party claim cited or `[unverified — verify at build via vega.github.io / deneb-viz.github.io]`. DoD: prettier-clean, claim-grounding markers present.

**Phase 2 — cross-surface spec-authoring skill (`ravenclaude-core`).** `skills/declarative-visualization/SKILL.md` — author a Vega-Lite/Deneb spec for a stated intent, on any surface; the 6-step method (pick Vega-Lite vs Vega; bind data per surface; encode; wire interactivity; test null/empty; verify via render loop); a `spec-patterns/` library of surface-agnostic Vega-Lite templates (diverging bar, dumbbell, small-multiples facet, heatmap, sparkline strip, annotated line) each with `data:{"name":"…"}` + a dummy `values` for local test; the **mandatory security-surface audit** (no `data.url`, no remote `$schema`, no network `transform.lookup`). DoD: all templates valid JSON; security audit documented; cites the knowledge file.

**Phase 3 — runnable security/quality linter + Gate 101 (`ravenclaude-core`).** `skills/declarative-visualization/lint.py` (stdlib-only, exit-coded, like `pbir-layout-engine`): asserts a spec/template has **no `data.url`**, **no remote `$schema`**, no network `transform.lookup`/`loader` override, and (for SVG) **no `<script>`/`on*` handlers**. Full Vega-Lite *schema* validation is **out** (needs a banned third-party dep; `visual-feedback-loop`'s render IS the schema check — both panels converged). **Gate 101** bidirectional + teeth (a mutant template with a `data.url` must fail), modeled on Gate 92/100. DoD: Gate 101 green + must-fail half proven.

**Phase 4 — cross-surface priors (every viz agent).** Conditional "Declarative visualization (Deneb/Vega-Lite/SVG)" prior pointing at the neutral skill, on: `power-platform/power-bi-engineer` (Deneb + SVG-in-DAX), `data-platform/dashboard-builder`, `tableau/tableau-viz-engineer`, `ravenclaude-core/frontend-coder`, `web-design/frontend-implementer`, `frontend-engineering/react-implementation-engineer`, and **`data-viz-designer` inherits when it lands**. Each degrades gracefully (guidance even without a render tool). DoD: grep-confirms each prior; merge-safety note on shared files.

**Phase 5 — coordinate with in-flight `data-viz-designer`.** Contract: data-viz-designer *invokes* `declarative-visualization` when chart-from-intent yields "core visual can't serve this"; it does not re-implement spec authoring. Merge-safe section boundaries on `power-bi-engineer.md` (this build + the queued phases-2-7 touch it in different sections).

**Phase 6 — regen + close-out.** Per-phase regen discipline: frontmatter-colon-quoting; bump ravenclaude-core skill-count string in plugin.json + marketplace.json; update the audit-gates skill-count fixture; regen dashboard.html / index.html / concepts / copilot package; version bump; full `audit-gates.sh` green (incl. Gate 101); prettier whole-tree; draft PR.

## Dependency DAG

```
P0 ──┬─► P1 (neutral knowledge) ──► P2 (skill + templates) ──► P3 (lint.py + Gate 101) ──► P4 (priors) ──► P6 (regen/PR)
     └─► P5 (data-viz-designer coordination) ── parallel; gates P4 merge-safety only
```
Critical path: P0→P1→P2→P3→P4→P6. P1↔P5 parallel. P4's per-agent priors parallelize.

## Alternatives (with trade-offs)

1. **Runnable linter scope:** security-only linter (chosen) vs full Vega-Lite schema validator. Chosen security-only — full schema validation needs a banned third-party dep; the render loop is the schema check.
2. **Home:** neutral `ravenclaude-core` (chosen, per owner directive) vs power-platform (Panel B) vs new plugin (rejected by both). Neutral wins on "available to any agent anywhere."
3. **Reviewer agent:** a dedicated `viz-spec-reviewer` (Panel A) vs the runnable linter + `visual-feedback-loop` (Panel B). Chosen: linter + render loop now; a reviewer agent only if volume proves it (defer).
4. **SVG:** SVG-in-DAX (power-platform knowledge, PBI-specific) vs standalone SVG (neutral skill). Both — the neutral skill owns standalone SVG; links to the PBI-specific SVG-in-DAX doc.

## Security (load-bearing — untrusted-input surface)

Vega/Vega-Lite specs and SVG are untrusted-input-shaped: Vega has a `loader` + `transform.lookup` external-URL vector; SVG can carry `<script>`/event handlers. Controls: Gate 101 enforces no-network-source + no-script in committed templates (the must-fail half is load-bearing); **any PR adding/modifying a `spec-patterns/*.json` or SVG template routes through `ravenclaude-core/security-reviewer`** (declared in the skill as an invariant). When reviewing a *user-supplied* spec, apply the allowlist before rendering.

## Coordination caveat

The queued `data-viz-designer` (phases 2–7) and this build both touch `power-platform/power-bi-engineer.md` in **different sections** (cross-link vs declarative-viz prior) — clean if whoever lands second applies to the updated file. Land `data-viz-designer` first if both are queued.

## Definition of done

Per-phase DoD above + the regen discipline (Phase 6) + Gate 101 bidirectional + security-reviewer gate on templates + full `audit-gates.sh` green + prettier whole-tree + cross-surface priors grep-confirmed on every named viz agent.

## Unverified claims to settle at build (G1 carry-over)

- Vega-Lite grammar specifics + the `loader`/`transform.lookup` surface → verify at vega.github.io.
- Deneb certified-build disables the loader → verify at deneb-viz.github.io / AppSource cert docs.
- Buhler's canonical Figma→SVG→PBI article 404'd → relocate the live article (data-goblins.com/articles) or reconstruct the technique from first principles + mark `[unverified — source 404'd]`.
- SVG-in-DAX char limit + `data:image/svg+xml;utf8,` prefix + PBI Image-visual rasterization-blocks-script → verify against current Power BI docs.
