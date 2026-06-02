# Strategic Plan — `data-viz-designer` agent for RavenClaude

> **Status:** v2 — gap-filled after panel review, 2026-06-02. Input for the build-plan phase of the two-panel-plan-review skill. Authored after two parallel deep-research streams (data-viz canon + agentic Power BI build patterns), one focused verification pass against primary sources, and Panel 1's four-lens stress test (architect, security, ops, devil's-advocate). All P0 and P1 gaps from Panel 1 are now resolved inline; surviving P2 gaps are folded in where they improve load-bearing clarity.

---

## 1. The problem we're solving

Matt is seeing AI-generated Power BI reports with **overlapping visuals**, **charts that don't match the data shape**, and **layouts that don't carry meaning**. The community has already named this failure mode — **"Power BI Slop"**, coined by Kurt Buhler / `data-goblin/power-bi-agentic-development` (663⭐, GPL-3.0, weekly cadence, professionally authored). The structural cause is that **no AI agent in this marketplace owns the visualization-design discipline as a domain-neutral capability**. The visualization canon (Tufte, Cleveland-McGill, Few, Cairo, Knaflic, Kirk, IBCS, FT Visual Vocabulary) exists; the engineering layer that prevents overlap exists; the accessibility floor (WCAG 2.2) exists. They are scattered, partially encoded in `plugins/tableau/`, and not invoked by the marketplace's Power BI or SaaS-dashboard agents.

The marketplace's existing surfaces:

- `plugins/power-platform/agents/power-bi-engineer.md` owns Power BI semantic models, DAX, PBIR file shape (via the just-shipped `pbir-enhanced-reference.md` + `pbir-enhanced-report-loading.md` + `sempy-fabric-reference.md` + `dax-category-name-mismatch-zero-scores.md`). **No design discipline.**
- `plugins/data-platform/agents/dashboard-builder.md` owns SaaS-dashboard work across Evidence / Superset / Metabase / Cube + React. **No design discipline beyond the JWT-flow security layer.**
- `plugins/tableau/best-practices/viz-*.md` (6 files) encode partial canon — Cleveland-McGill perceptual hierarchy, chart-type-by-question-class, axis integrity, color/accessibility, interactivity intent taxonomy — but only Tableau callers see them.
- `plugins/ravenclaude-core/agents/designer.md` owns UX direction for screens (apps, wireframes, slides, infographics). **Different deliverable shape — dashboards / charts / KPI tiles are not its scope.**

Microsoft's own first-party tooling does not cover this gap:

- **Power BI Copilot 2026** is intentionally narrow — explicitly does NOT support "styling or formatting changes" or "custom visuals" (verified verbatim against `learn.microsoft.com/en-us/power-bi/create-reports/copilot-create-reports`, page date 2025-11-13). It's a citizen-maker assistant, not a code-based engagement-engineer agent.
- **Tabular Editor BPA** ships 71 rules — **zero about visual layout, chart selection, color, or page composition** (verified against `microsoft/Analysis-Services/BestPracticeRules`). All 71 are semantic-model / DAX / measure-format-string rules.

This is the lane the new agent claims.

### 1.5 The case for not building this (devil's-advocate floor)

Before committing engineering effort, the alternatives this plan competes against:

| Alternative | What it is | Why we are rejecting it |
|---|---|---|
| **Do nothing** | Park the work; revisit when a real engagement demands it (the policy applied to the competitor-analysis plugin in MEMORY). | Power-BI-Slop output has now been observed by Matt in three distinct contexts this session (community-canon Buhler post + Researcher #2's verified inventory of 5 community skills converging on the same failure modes + Matt's own dogfooding). It is no longer a hypothetical n=1 — the failure mode is the most-cited gap in the agentic-Power-BI corpus the verification pass surveyed. The "park it" policy applies when the work is *speculative*; this work is *evidenced*. |
| **Inline prior + standalone linter only** | A 30-line knowledge prior added to `power-bi-engineer.md` + the Tier 1 linter shipped as a `scripts/` utility. No new agent, no skill scaffolding, no Tableau churn. | Captures ~40% of the upside (layout-arithmetic floor only). Misses the chart-from-intent decision tree, the IBCS opt-in path, the WCAG floor, the cross-tool transfer to `dashboard-builder`, and the canon-of-record consolidation the Tableau promotion delivers. Acceptable as a fallback if v0.1.0 budget overruns (see §7 cut-list). |
| **Extend `ravenclaude-core/designer`** | Add a chart-design sub-rubric to the existing screen-design agent. | The two deliverable shapes have different rubrics (a chart-from-intent decision is not a wireframe; a KPI-tile-grid is not a slide layout), different downstream consumers (`power-bi-engineer` + `dashboard-builder` vs `designer`'s screen callers), and different review patterns. Forcing them into one agent re-creates the dispatch ambiguity Panel 1's architect lens flagged — and `designer.md` would grow past its current focused scope. |

**What this PR displaces from the queue:** the v0.101.0 follow-ups parked in MEMORY (CSRF, port check, posture size cap, Content-Length try/except, audit-gates fixtures for schema gate, knowledge-health dashboard card, STRATEGY.md content, CLAUDE.md stale-recipe refresh) are not addressed by this PR. The build plan declares this opportunity cost explicitly and Matt should weigh it before approving.

---

## 2. What we're building

### 2.1 The agent

`plugins/ravenclaude-core/agents/data-viz-designer.md` — owns the *design layer*, with stack-specific implementation strings dispatched at invocation time. Owns:

1. **Chart-from-intent decisions** — given a user intent (Deviation / Correlation / Ranking / Distribution / Change-over-Time / Magnitude / Part-to-whole / Flow / Spatial — the FT Visual Vocabulary 9-category taxonomy) and a data shape (cardinality, dimensionality, hierarchy, temporality), recommend a chart family. **Dispatch contract (added per architect gap `arch-3`):** the calling agent (`power-bi-engineer`, `dashboard-builder`, or any other) MUST pass a `--stack=pbir|tremor|recharts|evidence|superset|metabase` declaration (or equivalent in-prompt statement) when invoking. Absent that, the agent returns the intent-→-chart-family decision only (FT category name + chart-family name + Cleveland-McGill rank) and refuses to emit stack-specific strings. Fail-loud refusal, not silent guess.
2. **Page composition + layout** — the 3-30-300 detail gradient (top-left summary, bottom-right detail, 3s/30s/300s viewing distances), the "measure the scaffold first" rule, the `(page_w, page_h, margin, gap, n_cols, n_rows)` arithmetic that prevents overlap by construction.
3. **Color + accessibility** — WCAG 2.2 SC 1.4.3 / 1.4.6 / 1.4.11 contrast floors (verified verbatim against `w3.org/TR/WCAG22/`), ColorBrewer qualitative / sequential / diverging palette guidance, colorblind-safe defaults (blue/orange; ColorBrewer Set2 / Dark2 / Paired).
4. **Anti-pattern detection** — the AI-generated-layout-failure catalog (overlap, default-theme, all-bar-charts, bare-KPI, truncated y-axes, etc.). Each pattern: detector + severity + fix. Public-facing description uses the neutral phrasing **"AI-generated Power BI layout failures"** (per devil's-advocate gap `naming-1`); the anti-pattern catalog file's header cites **"Power BI Slop (Kurt Buhler, data-goblin)"** once as the community term that named the failure mode, preserving the credibility benefit without the prospective-client-facing risk.
5. **IBCS opt-in mode** — when the engagement triggers IBCS (see §2.7 for the precedence-resolved trigger rules), opt into the SUCCESS rules (Say / Unify / Condense / Check / Express / Simplify / Structure) and the IBCS notation (actual = solid black, **PY = solid medium-gray**, plan = outlined, **forecast = hatched** — verified against `ibcs.com/standards`).

**Boundary with `ravenclaude-core/designer` — concrete dispatch table (added per devil's-advocate gap `boundary-1`):**

| Example request | Route to | Rationale |
|---|---|---|
| "Build a Power BI report page" | `data-viz-designer` | Charts + KPI tiles + layout arithmetic — data-viz core scope |
| "Build a Power Apps screen" | `designer` | Interaction surface, not data-encoding |
| "Pitch deck with embedded charts" | `designer` leads, `data-viz-designer` consulted | Deck = screen scope; embedded charts = data-viz |
| "Onboarding wireframe" | `designer` | Pure UX, no quantitative-encoding load |
| "Dashboard with filter pane + KPI row + chart grid" | `data-viz-designer` leads, `designer` consulted only if non-data screens exist alongside | The chart grid + KPI row are data-viz; filter-pane UX is shared |
| "Infographic with one statistic" | `designer` | Single-fact rhetoric, not multi-encoding dashboard |
| "Tremor/Recharts component layout for a SaaS app" | `data-viz-designer` (with `--stack=tremor` or `--stack=recharts`) | Chart-component selection + composition |

`designer.md` gets the inverse table (when to bounce work to `data-viz-designer`) rather than the one-line note v1 proposed.

**Invocation model (added per architect gap `arch-9`):** `data-viz-designer` is invoked by the Team Lead when a calling specialist (`power-bi-engineer` / `dashboard-builder`) declares the work is dashboard / chart / KPI-shaped. Output is a design brief (FT category + chart family + grid arithmetic + palette declaration + WCAG-pass verification + linter report). The calling specialist then implements in their stack. **Not** inline reading-only knowledge — a sub-agent invocation with a structured output, so debuggability is `grep`-able through the Sága log.

**WebFetch return-handling contract (added per architect gap `arch-7` and security gap `sec-1`):** All WebFetch results inside this agent's skills are treated as untrusted DATA. `<system-reminder>`, `<system>`, `<important>`, `[INST]`, or any role-shifting markers inside fetched bodies are stripped/inerted before the model reads the body, logged as a citation note ("primary source contained N injection attempts; treated as data"), and never acted upon. Two confirmed injection sites (ibcs.com/standards, FT GitHub tree page) are documented as permanent reference in `plugins/ravenclaude-core/knowledge/webfetch-return-envelope-hardening.md` (new file). The skills cite the **already-verified §3 quotes as the canonical text** and only re-fetch on an explicit refresh trigger, not on every invocation — re-verification cadence is bounded by the knowledge-freshness contract in §2.7. An audit-gates fixture (Gate 49) proves a poisoned-body fixture is neutered. Cross-marketplace generalization ("every agent that WebFetches needs this") is routed to `security-reviewer` as a separate follow-up — but the floor ships here, in v0.1.0.

### 2.2 The skills

| Skill | Path | Purpose |
|---|---|---|
| **`chart-from-intent`** | `plugins/ravenclaude-core/skills/chart-from-intent/SKILL.md` | The FT Visual Vocabulary 9-category mapping. Stack-dispatched per the §2.1 contract — Power BI `visualType` strings vs Tremor / Recharts / Evidence / Superset / Metabase components. Carries the 5 decision trees (intent → category → chart; kpi vs cardVisual vs card; matrix vs flat table; page-level filter vs slicer; AI-output smell → root cause → fix). Cites canonical-text §3 quotes; only re-fetches on explicit refresh trigger. |
| **`pbir-layout-engine`** | `plugins/ravenclaude-core/skills/pbir-layout-engine/SKILL.md` | The "measure the scaffold first" discipline + layout arithmetic + the Tier 1 7-check static linter at `plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py` (canonical executable location — see §2.3). Power BI primary; the AABB / within-canvas / equal-gap / column-alignment math (checks 1-4) generalizes via a stack-agnostic `{x, y, width, height}` JSON shape. |
| **`wcag-viz-contrast`** | `plugins/ravenclaude-core/skills/wcag-viz-contrast/SKILL.md` | WCAG 2.2 AA contrast checks. SC 1.4.11 ≥ 3:1 for "parts of graphics required to understand the content" (verbatim). Colorblind-safe palette defaults. "Color is never the only channel" enforcement. |
| **`ibcs-variance-reports`** | `plugins/ravenclaude-core/skills/ibcs-variance-reports/SKILL.md` | **Opt-in.** SUCCESS rules, IBCS notation (corrected: PY = solid medium-gray, Forecast = hatched). 4 variance-chart templates. Triggered per the precedence-resolved rules in §2.7. Emits a one-line "IBCS mode active — triggered by `<source>`" breadcrumb in every output where engaged, so the activation surface is never silent. |

### 2.3 The knowledge files + executable

| File | Path | Purpose |
|---|---|---|
| **`visual-design-decision-trees.md`** | `plugins/ravenclaude-core/knowledge/visual-design-decision-trees.md` | 5 decision trees, Mermaid-rendered. Edits anchor on the BMA CSP lesson's editorial bar (the `dax-category-name-mismatch-zero-scores.md` shape). |
| **`power-bi-slop-anti-patterns.md`** | `plugins/ravenclaude-core/knowledge/power-bi-slop-anti-patterns.md` | The 16-row anti-pattern catalog. Each row: pattern / detector / severity / fix. Header cites "Power BI Slop (Kurt Buhler, data-goblin)" once as the community-canonical term. Cites community sources (data-goblin, lukasreese, wardawg, MinaSaad1) with URL + verified-on date + commit SHA per security gap `sec-6`. Includes the verified contoso-examples horizontal-grid finding (24px margin + 16px gutter + 312px stride). |
| **`webfetch-return-envelope-hardening.md`** | `plugins/ravenclaude-core/knowledge/webfetch-return-envelope-hardening.md` | Documents the WebFetch return-handling contract (§2.1) + the two confirmed injection sites (ibcs.com/standards, FT GitHub tree page) as a permanent reference for any agent that WebFetches canon sources. |
| **`pbir-design-lint.py`** (executable, canonical home) | `plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py` | The Tier 1 7-check static linter as runnable code. **Single executable, two callers, zero re-implementations** (per architect gap `arch-1`). Both the agent's in-loop call and `scripts/audit-gates.sh` Gate 48 invoke `python3 plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py <fixture-dir>` — no copy, no shim. Co-located with the skill that documents it. **Purity contract (per security gap `sec-2`):** deterministic, no network, no subprocess, no eval; reads only paths passed via argv; rejects argv paths containing `..` or absolute paths outside the repo root; exits non-zero on any I/O error rather than partial-pass. Contract appears as the file's docstring AND as a row in `power-bi-slop-anti-patterns.md` so it's part of the audit-gates fixture surface. |
| **`pbir-design-lint.md`** (companion doc) | `plugins/ravenclaude-core/knowledge/pbir-design-lint.md` | Documents the linter's contract for human readers and other agents. Points at the canonical executable in `skills/pbir-layout-engine/lint.py`. No code duplication. |

`.repo-layout.json` `allowed_globs` updated to permit `plugins/*/skills/*/*.py` and `plugins/*/knowledge/*.py` (the latter is empty for now but reserved); `tests/fixtures/data-viz/**` is added explicitly per security gap `sec-5`.

### 2.4 Tableau promotions to core (with anti-drift gate)

4 best-practices in `plugins/tableau/best-practices/` have domain-neutral cores. Promote those cores to `plugins/ravenclaude-core/best-practices/`; the surviving Tableau files become **thin pointers** that include a one-line `> Canonical canon: see ravenclaude-core/best-practices/<file>.md` reference and contain ONLY Tableau-specific deltas — no duplicated canon paragraphs.

| Promote (new file in core) | Source (stays in tableau, thin — pointer + Tableau-specific delta only) |
|---|---|
| `chart-type-follows-the-question.md` (Cleveland-McGill + question-class taxonomy + pie-only-2-or-3-slices) | `plugins/tableau/best-practices/viz-chart-type-follows-the-question.md` |
| `axis-integrity.md` (zero baseline for length encodings; dual-axis sync; ≤2-points-is-not-a-trend) | `plugins/tableau/best-practices/viz-axis-and-dual-axis-integrity.md` |
| `color-and-accessibility.md` (colorblind-safe palette + "color is never the only channel" + WCAG 1.4.11) | `plugins/tableau/best-practices/viz-formatting-and-accessibility.md` |
| `interactivity-intent-taxonomy.md` (scope / emphasize / swap / select-vs-rest) | `plugins/tableau/best-practices/viz-actions-and-interactivity.md` |

Plus from `plugins/tableau/knowledge/viz-calc-decision-trees.md`, promote two trees (chart-type-by-question-class tree, interactivity-mechanism tree) to the new `visual-design-decision-trees.md`; the LOD / FIXED-vs-INCLUDE-vs-EXCLUDE trees stay (Tableau calc-engine semantics).

**Anti-drift gate (added per architect gap `arch-6`):** an audit-gates check (Gate 50) flags any `tableau/best-practices/viz-*.md` file that grows back past **30 lines of overlap** with its canonical core counterpart, measured by a normalized text-similarity check. Forces the thin-pointer pattern to stay thin. Prevents silent canon-of-record drift six months from now.

**Breaking-change check (resolution per devil's-advocate gap `additive-1`):** the tableau promotion is *not* purely additive — it reorganizes the canon-of-record of another plugin. Resolution:

- The tableau plugin bumps **`tableau` 0.X.Y → 0.X.(Y+1)` (patch)** — the *content* hasn't broken (Tableau-specific deltas remain in place) but the *self-description* has shifted (canon-of-record now lives in core).
- **Migration note (consumer-facing):** "If you installed `tableau` without `ravenclaude-core`, the `viz-*.md` files now point at `ravenclaude-core/best-practices/*.md` for canon-of-record; install `ravenclaude-core` to get the full canon, or rely on the Tableau-specific deltas which remain in place. No breakage; cross-references are advisory."
- Consumers who installed `tableau`-only see a one-line pointer to a file they don't have — degraded readability, not breakage. Documented as a migration note in the tableau plugin's release notes.

### 2.5 Cross-links

- `plugins/power-platform/agents/power-bi-engineer.md` — inline knowledge prior added pointing at `ravenclaude-core/agents/data-viz-designer.md` and the 4 skills + 3 knowledge files. Includes the dispatch contract: "when invoking, pass `--stack=pbir`."
- `plugins/power-platform/CLAUDE.md` §8a — new row in the knowledge-bank table for the visual-design references.
- `plugins/data-platform/agents/dashboard-builder.md` — inline knowledge prior added pointing at the same. Includes the dispatch contract: "when invoking, pass `--stack=tremor|recharts|evidence|superset|metabase` as applicable."
- `plugins/data-platform/CLAUDE.md` §8a equivalent (if it has one) — same.
- `plugins/ravenclaude-core/agents/designer.md` — the inverse dispatch table from §2.1 replaces the one-line note v1 proposed.

### 2.6 Versioning

- `ravenclaude-core`: 0.108.0 → **0.109.0** (1 agent + 4 skills + 4 knowledge files including the new webfetch-hardening reference and pbir-design-lint.md companion + 4 promoted best-practices + 1 canonical executable under skills/). The ravenclaude-core additions are truly additive. Non-breaking. Plugin description updated.
- `power-platform`: 0.21.0 → **0.21.1** (cross-link + dispatch-contract addition; pure description / agent-prior change). Non-breaking.
- `data-platform`: current → **+0.0.1** (cross-link + dispatch-contract addition). Non-breaking.
- `tableau`: **+0.0.1 (patch)** with migration note per §2.4. The thin-pointer pattern means content semantics shifted but mechanics did not.

### 2.7 What ships in v0.1.0 vs deferred

**v0.1.0 (the next PR, this proposal):**
- Agent + 4 skills + 4 knowledge files (including `webfetch-return-envelope-hardening.md` + `pbir-design-lint.md`) + 4 promoted best-practices + cross-links + version bumps in 4 plugins.
- Tier 1 7-check static linter ships runnable at `plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py` (canonical, single-executable). **Fixtures** in `tests/fixtures/data-viz/` cover all 7 checks bidirectionally per architect gap `arch-5` — good fixture for all 7 + bad fixture for each (overlap, out-of-canvas, unequal-gap, column-misaligned, empty-bindings, theme-override-explosion, bad-schema with unknown `visualType`, bad-schema with invalid `displayOption`). Plus a `hand-tuned-vertical-grid-passes.json` fixture per devil's-advocate gap `linter-1` covering the verified contoso-examples vertical-row pattern.
- **Linter false-positive suppression (per devil's-advocate gap `linter-1`):** a `_lintConfig` block per page allowing `tolerance.equal_gap_px`, `tolerance.column_align_px`, and a per-visual `_lintIgnore: ["check-3", "check-4"]` array for documented intentional grid breaks. Default tolerances: ±4px (matches verified contoso-examples horizontal grid).
- **Schema-enum drift gate (per architect gap `arch-2`):** `lint.py` parses the `visualType` and `displayOption` enum lists directly from `plugins/ravenclaude-core/knowledge/pbir-enhanced-reference.md` § 1 at runtime — single source of truth, fail-loud on parse error. The PBIR Enhanced schema version (`visualContainer/2.7.0`) is pinned as a constant in `lint.py` with a comment naming what to update when it bumps. Audit-gates Gate 51 fails on a fixture where the reference file's enum list and the hand-extracted list (if any) drift.
- Honesty markers throughout. Every Microsoft Learn claim carries its `ms.date`. Every Medium-confidence canon claim carries `[unverified — training knowledge]`. Every verified community citation gets a URL + verified-on date + commit SHA per security gap `sec-6`.
- IBCS skill ships opt-in. **Precedence-resolved trigger rules (per architect gap `arch-4` and devil's-advocate gap `ibcs-1`):**
  - **Highest precedence:** explicit user request (positive OR negative). User "no IBCS" always wins, even if the environment-context tag is set.
  - **Next:** explicit "IBCS" mention in the prompt.
  - **Lowest:** `finance_context: ibcs` tag in `.ravenclaude/environment-context.md` (auto-discovered via the existing `environment-discovery` skill). Activates ONLY if neither of the above is set.
  - **The `environment-context.md` schema is defined in this PR.** The `environment-discovery` skill already exists per MEMORY and ravenclaude-core; this PR formalizes the `finance_context` key. Default value: unset. PR-reviewable change, not a per-invocation override.
  - **On activation**, the skill logs a single grep-able line to its output: `IBCS mode active — triggered by <user_request|explicit_mention|finance_context_tag>`. When the finance-context tag is the trigger (not the user prompt), the skill ALSO writes a Sága log entry under `.ravenclaude/runs/data-viz/ibcs-activations/<timestamp>.md` so silent activation has an audit trail.
  - **Fixture tests for the four trigger paths:** explicit-user-request-positive, explicit-user-request-negative-override, explicit-IBCS-mention, finance-context-tag-only.
- **Cross-page palette/typography consistency is NOT enforced in v0.1.0** (per architect gap `arch-8`). Caller must reuse the same palette declaration across pages. The agent description AND the `chart-from-intent` skill's preamble state this v0.1.0 limitation explicitly so v0.2.0's lint addition isn't experienced as a silent regression.
- **Public-facing failure-mode naming** uses neutral "AI-generated Power BI layout failures" (per devil's-advocate gap `naming-1`). The community term "Power BI Slop (Kurt Buhler, data-goblin)" is cited once in the anti-pattern catalog header.
- **Knowledge-freshness contract (per devil's-advocate gap `verification-1`):** every dated verbatim claim carries an inline `[verified YYYY-MM-DD]` marker. The agent's own contract requires re-verifying any claim older than **90 days** before quoting it in a deliverable. Wires into the deferred knowledge-health dashboard card (v0.101.0 follow-up) so stale claims surface on the dashboard. Without this, the v0.1.0 ships with built-in decay.

**v0.2.0 (deferred — separate PR with explicit security pre-requisites):**
- **Tier 3 render-verification loop** — Fabric REST `Reports - Export To File In Group` flow (verified pattern: 202 Accepted → poll `GetExportToFileStatus` → download from `resourceLocation` on `Succeeded`). Hand to a vision-capable LLM (or Matt's eyeball) for visual QA. Wire into `power-platform/agents/power-platform-tester.md` coverage.
- **v0.2.0 security pre-requisites (per security gap `sec-3`)** — must be addressed before v0.2.0 PR can merge:
  1. **Token acquisition pattern** — cite the `dataverse-token-acquisition-plan` precedent from MEMORY. Choose SPN or user OAuth; document where the token lives (env var? `.ravenclaude/`?).
  2. **`resourceLocation` is a bearer secret** — never log, never echo in agent transcripts, scrub from any error envelope. ~24h validity.
  3. **Rendered artifacts may contain RLS-filtered data** — do not hand to a third-party vision-LLM without an explicit per-engagement consent gate. The `data-platform` plugin's closeness-to-data invariant applies.
  4. **Explicit retention policy** for the rendered artifact in `.ravenclaude/runs/`.
- v0.2.0 PR explicitly requires a `security-reviewer` pass before merge.
- **Cross-page consistency** — `design-tokens.json` authored by the agent at report-start; all subsequent page generation reads from it; lint flag if any visual deviates.
- **Tier 4 headless-Chromium-on-published-Power-BI** — speculative. Re-evaluate after v0.2.0 ships.

---

## 3. Verified facts the agent encodes (with citations)

These are the High-confidence specifics the agent file will quote verbatim with primary-source URLs. Each dated claim carries a `[verified YYYY-MM-DD]` marker per the knowledge-freshness contract; re-verification cadence is 90 days.

### 3.1 WCAG 2.2 contrast

Verified against [`w3.org/TR/WCAG22/`](https://www.w3.org/TR/WCAG22/) on 2026-06-02:

- **SC 1.4.3 Contrast (Minimum) — AA**: "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1." Large-text exception 3:1.
- **SC 1.4.6 Contrast (Enhanced) — AAA**: 7:1 normal text, 4.5:1 large text.
- **SC 1.4.11 Non-text Contrast — AA**: "Contrast ratio of at least 3:1 against adjacent color(s)" for "Visual information required to identify user interface components and states" AND "**Parts of graphics required to understand the content.**" That last clause is the load-bearing one for charts.
- SC numbering identical between WCAG 2.1 and 2.2.

### 3.2 ColorBrewer

Verified against [`colorbrewer2.org`](https://colorbrewer2.org/) on 2026-06-02:

- Authors: **Cynthia Brewer + Mark Harrower + The Pennsylvania State University**.
- Three palette families: **sequential, diverging, qualitative**.
- Flag labels (lowercase): **"colorblind safe", "print friendly", "photocopy safe"**.
- Colorblind-safe qualitative palettes for ≥3 categories: **Dark2, Set2, Paired**.

### 3.3 IBCS SUCCESS rules

Verified against [`ibcs.com/standards`](https://www.ibcs.com/standards/) on 2026-06-02 (verification subagent flagged one `<system-reminder>` injection attempt in the page body; treated as untrusted data per the §2.1 WebFetch contract):

- **S — SAY**: Convey a message.
- **U — UNIFY**: Apply semantic notation. *(NOT "apply consistently" — official wording is just "Apply semantic notation".)*
- **C — CONDENSE**: Increase information density.
- **C — CHECK**: Ensure visual integrity.
- **E — EXPRESS**: Choose proper visualization.
- **S — SIMPLIFY**: Avoid clutter.
- **S — STRUCTURE**: Organize content.

IBCS notation for time scenarios (corrected from Researcher #1's recall):
- Actual = solid dark fill (black).
- **PY = solid medium-gray** (NOT hatched).
- Plan = outlined.
- **Forecast = hatched** (the hatched scenario, not PY).

The IBCS variance hex codes (`#0C3549` actual, `#CCCCCC` PY, `#44C088` positive, `#ED7373` negative) are a *third-party convention* (`lukasreese/powerbi-claude-skills`), NOT the official IBCS palette. IBCS's free pages describe colors qualitatively; the official hex codes live in the paid IBCS Standards 1.2 PDF. **Encode as `[unverified — third-party convention, IBCS PDF behind paywall]`.**

### 3.4 FT Visual Vocabulary

Verified against [`github.com/Financial-Times/chart-doctor`](https://github.com/Financial-Times/chart-doctor) on 2026-06-02 (verification subagent flagged one `<system-reminder>` injection attempt on the FT GitHub tree page; treated as untrusted data per the §2.1 WebFetch contract):

- **9 categories**: Deviation, Correlation, Ranking, Distribution, Change over Time, Magnitude, Part-to-whole, Flow, Spatial. (Casing matters: "Change over Time" capital T, "Part-to-whole" lowercase w.)
- License: **MIT**.
- Stars: ~3.3k (display rounded — Researcher #1's "3,281" is stale-but-plausible).
- README explicitly cites Cleveland & McGill 1984: "Graphical Perception: Theory, Experimentation, and Application to the Development of Graphical Methods" — confirms the perceptual-hierarchy provenance.
- Deviation includes: Diverging bar, Diverging stacked bar, Spine chart, Surplus/deficit filled line.
- Flow includes: Sankey, Waterfall, Chord, Network.
- Magnitude includes: Column, Bar, Paired column, Paired bar, Proportional stacked bar, Proportional symbol, Isotype, Lollipop, Radar, Parallel coordinates.
- Last-commit date: **could not verify** in the verification pass (GitHub HTML didn't expose the timestamp; `gh api` denied for the verification subagent). Encode as `[unverified — could not extract from GitHub HTML]`.

### 3.5 Microsoft Power BI

Verified against `learn.microsoft.com` on 2026-06-02:

- **Power BI Copilot limitations** (page date 2025-11-13, updated 2025-11-18, [`copilot-create-reports`](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-create-reports)):
  - Verbatim: "**Styling changes**: Styling or formatting changes aren't supported through Copilot."
  - Verbatim: "**Custom visuals**: Custom visuals aren't currently supported."
- **Canvas size** (page date 2026-04-13, [`power-bi-report-display-settings`](https://learn.microsoft.com/en-us/power-bi/create-reports/power-bi-report-display-settings)): **16:9 is the default aspect ratio**; 1280×720 is the smallest of four standard 16:9 sizes. (Researcher #1's "1280×720 default" is an oversimplification.)
- **`displayOption`**: JS SDK enum values **`FitToPage` / `FitToWidth` / `ActualSize`** (PascalCase). UI labels are **"Fit to page" / "Fit to width" / "Actual size"** (space-separated). Both surfaces matter.
- **Q&A visual deprecation**: announced December 2025; full retirement **December 2026** (from Power BI Updates Blog "Deprecating Power BI Q&A"). Agent should not generate `qnaVisual`.
- **Reports - Export To File In Group** REST endpoint ([Learn API ref](https://learn.microsoft.com/en-us/rest/api/power-bi/reports/export-to-file-in-group)): asynchronous. POST → 202 Accepted with `Export` object (`id`, `status`, `resourceLocation`). Poll `GetExportToFileStatus`. ExportState enum: `Undefined / NotStarted / Running / Succeeded / Failed`. On `Succeeded`, GET from `resourceLocation`. Verified pattern.

### 3.6 contoso-examples grid

Verified against [`bernatagulloesbrina/contoso-examples`](https://github.com/bernatagulloesbrina/contoso-examples) on 2026-06-02 by reading 7 of 9 `visual.json` files on the Overview page:

- **Horizontal grid**: 24px page margin + 16px gutter between KPI tiles + 312px stride (KPI width 296 + gutter 16). KPI row x-values 24, 336, 648, 960 — perfectly regular. **Verified.**
- **Vertical grid**: NOT on a fixed 8/16/24px step. Title at y=20, KPI row at y=120, sales-trend at y=276, by-brand at y=532. Differences 100, 156, 256 — row-height-driven, content-tuned. **Encode as "horizontal grid verified; vertical hand-tuned per row."** This is the canonical fixture for the linter's `hand-tuned-vertical-grid-passes.json` suppression-mechanic test.
- Title outlier: (20, 20) vs the rest at (24, 24) baseline. Authoring inconsistency.

### 3.7 Cleveland-McGill replication

Verified DOIs on 2026-06-02:

- **Heer & Bostock (2010)** — "Crowdsourcing Graphical Perception: Using Mechanical Turk to Assess Visualization Design." CHI 2010, pp. 203-212. DOI [10.1145/1753326.1753357](https://doi.org/10.1145/1753326.1753357). CHI 2010 Best Paper nominee. Broadly confirmed the original ranking.
- **Saket, Endert, Demiralp (2018)** — "Task-Based Effectiveness of Basic Visualizations." IEEE TVCG. DOI [10.1109/TVCG.2018.2829750](https://doi.org/10.1109/TVCG.2018.2829750). Epub 2018-05-04; print issue July 2019. Pie/donut perform comparably to bar for *single-percentage* estimation tasks; bars dominate for rank/comparison.
- **Bateman et al. (2010)** — "Useful Junk? The Effects of Visual Embellishment on Comprehension and Memorability of Charts." CHI 2010, pp. 2573-2582. DOI [10.1145/1753326.1753716](https://doi.org/10.1145/1753326.1753716). Authors: S. Bateman, R. L. Mandryk, C. Gutwin, A. Genest, D. McDine, C. Brooks. Caveat to chartjunk-is-always-bad.

### 3.8 Community-skill sources (verified by Researcher #2 via `gh api`)

All verified real, active, and content-as-described. Per security gap `sec-6`, citations pin to commit SHA at verification date; staleness is acceptable, drift without re-verification is not.

- **`data-goblin/power-bi-agentic-development`** (663⭐, GPL-3.0). Skills: `plugins/reports/skills/pbi-report-design/`, `references/{layout-guidelines,cards-and-kpis,tables-and-matrices,visual-colors,page-titles}.md`. Coined "Power BI Slop." [verified 2026-06-02 at commit SHA pinned in build plan]
- **`lukasreese/powerbi-claude-skills`** (73⭐). IBCS-aware `pbir-report-builder` skill + 4 IBCS variance templates + the (third-party) `#0C3549`/`#CCCCCC`/`#44C088`/`#ED7373` palette. [verified 2026-06-02]
- **`wardawgmalvicious/claude-config`** (~30 PBIR skills). The "measure the scaffold first" 10-step `pbir-report-workflow`. [verified 2026-06-02]
- **`MinaSaad1/pbi-cli`** (344⭐, MIT). Python CLI + Claude Code skills; dual-layer (TOM + PBIR). [verified 2026-06-02]
- **`TemplateMechanics/pbi-pilot`** (0⭐ but concrete). The 2-step open+refresh sequence + "NEVER invent PBIR queryState structures" rule. [verified 2026-06-02]
- **`microsoft/Analysis-Services/BestPracticeRules`** (71 rules, zero about visual layout — verified the structural gap). [verified 2026-06-02]
- **`Financial-Times/chart-doctor/visual-vocabulary`** (~3.3k⭐, MIT). Canonical 9-category intent taxonomy. [verified 2026-06-02]

---

## 4. The Tier 1 static linter (7 checks)

Runnable Python module shipped at the canonical path `plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py` (per architect gap `arch-1`). The agent runs it on every `visual.json` set it authors before declaring done. `scripts/audit-gates.sh` Gate 48 invokes the same single executable. Drop-in for any caller's verification loop.

| # | Check | Rule | Source |
|---|---|---|---|
| 1 | **No-overlap (AABB)** | For each pair of visuals on a page: `not (a.x + a.width > b.x AND b.x + b.width > a.x AND a.y + a.height > b.y AND b.y + b.height > a.y)` | wardawg `pbir-report-workflow` Rule 1 |
| 2 | **Within-canvas** | For each visual: `position.x + position.width <= page.width AND position.y + position.height <= page.height` | data-goblin Object-Model validates this; we lift it forward |
| 3 | **Equal-gap (horizontal)** | For each row of visuals at the same y, the gaps between adjacent visuals are within ±4px of each other (configurable via `_lintConfig.tolerance.equal_gap_px`) | data-goblin layout-guidelines |
| 4 | **Column-alignment (vertical)** | For visuals in different rows that should share a column, their `x` and `x + width` values are equal (configurable via `_lintConfig.tolerance.column_align_px`) | data-goblin layout-guidelines |
| 5 | **No-empty-binding** | Every data visual has at least one `queryState.<role>.projections[]` populated | data-goblin pbi-report-design Objective Checklist |
| 6 | **Theme-compliance (count override entries)** | Count `objects` + `visualContainerObjects` entries; flag visuals with > N (suggests un-promoted formatting that should move to theme) | data-goblin modifying-theme-json Audit workflow |
| 7 | **Schema-valid** | `$schema` matches the pinned `visualContainer/2.7.0` constant; `visualType` is in the enum set **parsed at runtime from `pbir-enhanced-reference.md` § 1**; `displayOption` is a string from the enum set parsed at runtime. Fail-loud on parse error. | Existing `pbir-enhanced-reference.md` + pinned schema-version constant |

**Cross-stack scope (per devil's-advocate gap `domain-neutral-1`):** checks 1-4 (overlap, within-canvas, equal-gap, column-alignment) operate on a stack-agnostic `{x, y, width, height}` JSON shape and run against any caller's layout artifact. Checks 5-7 (queryState, theme-objects, $schema/visualType/displayOption) are PBIR-specific and skip silently with a single info-line for non-PBIR inputs. The linter's domain-neutral arithmetic core lives in `plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py` as `layout_arithmetic_checks(visuals: list[dict]) -> list[Finding]`; the PBIR-specific checks are gated behind a `--pbir` flag (default ON when invoked on a PBIR fixture by virtue of detecting `$schema`).

**The agent's promise is reworded** (per devil's-advocate gap `linter-1`) to match what the linter actually verifies: overlap, within-canvas, alignment-by-construction, schema-compliance. Chart-type-mismatch and semantic-layout failures are caught only by in-loop agent reasoning + the deferred Tier 3 render-verification — the agent description states this explicitly.

**Suppression mechanic (per devil's-advocate gap `linter-1`):** a `_lintConfig` block per page allows:
- `tolerance.equal_gap_px` (default 4)
- `tolerance.column_align_px` (default 0 — strict equality)
- per-visual `_lintIgnore: ["check-3", "check-4"]` array for documented intentional grid breaks

**Fixtures (Tier 1 audit-gates discipline — bidirectional coverage of all 7 checks per architect gap `arch-5`):**

| Fixture | Purpose |
|---|---|
| `tests/fixtures/data-viz/good-page.json` + 4 `visual.json` files | Passes all 7 checks |
| `tests/fixtures/data-viz/bad-page-overlap.json` | Fails check 1 |
| `tests/fixtures/data-viz/bad-page-out-of-canvas.json` | Fails check 2 |
| `tests/fixtures/data-viz/bad-page-unequal-gaps.json` | Fails check 3 |
| `tests/fixtures/data-viz/bad-page-column-misaligned.json` | Fails check 4 (added per `arch-5`) |
| `tests/fixtures/data-viz/bad-page-empty-bindings.json` | Fails check 5 |
| `tests/fixtures/data-viz/bad-page-theme-override-explosion.json` | Fails check 6 (added per `arch-5`) |
| `tests/fixtures/data-viz/bad-page-bad-schema-unknown-visualType.json` | Fails check 7 (added per `arch-5`) |
| `tests/fixtures/data-viz/bad-page-bad-schema-invalid-displayOption.json` | Fails check 7 second arm (added per `arch-5`) |
| `tests/fixtures/data-viz/hand-tuned-vertical-grid-passes.json` | Verified contoso-examples vertical pattern PASSES (suppression-mechanic test, per `linter-1`) |
| `tests/fixtures/data-viz/poisoned-fetched-body.json` | Injected `<system-reminder>` in fetched-body fixture is neutered (WebFetch hardening, per `sec-1`) |
| `tests/fixtures/data-viz/enum-drift-divergence.json` | Reference-file enum and hand-extracted enum diverge (schema-drift, per `arch-2`) |

`.repo-layout.json` `allowed_globs` updated to include `tests/fixtures/data-viz/**` AND `plugins/*/skills/*/*.py` BEFORE the fixtures land. Audit-gates Gate 48 fixture includes a "gate runs" assertion (not just "passes on good / fails on bad") — a smoke test that Gate 48 was actually invoked, not skipped. Cross-references `docs/best-practices/ci-gate-audit.md`.

Gate 48 in `scripts/audit-gates.sh` proves each of the 7 checks fails on bad and passes on good. Gate 49 proves the WebFetch poisoned-body fixture is neutered. Gate 50 proves the tableau anti-drift check fires when a thin pointer regrows past 30 lines of overlap. Gate 51 proves the schema-enum drift check fires when the reference file and the linter's runtime parse diverge.

**Not v0.1.0 (Tier 2/3/4):**
- Tier 2 — DAX correctness via Fabric REST `executeQueries` (already covered by the BMA CSP lesson; no new work needed).
- Tier 3 — Render via Fabric REST `Reports - Export To File In Group` (deferred to v0.2.0 with security pre-requisites per §2.7).
- Tier 4 — Headless Chromium on published Power BI (speculative).

---

## 5. The decisions Panel 1 stress-tested (and how this v2 plan resolves them)

Panel 1 reviewed v1 against four lenses (architect, security, ops, devil's-advocate). v2 resolves all P0 and P1 gaps inline. Surviving open question routes are surfaced for the build-plan panel.

1. **Boundary cleanliness between `data-viz-designer` and `ravenclaude-core/designer`** — RESOLVED via the concrete 7-row dispatch table in §2.1, plus the inverse table added to `designer.md`. No longer a one-line note.
2. **Cross-tool transfer honesty** — RESOLVED via the stack-dispatch contract in §2.1 (caller MUST pass `--stack=...`; absent that, the agent returns stack-agnostic design only). Linter checks 1-4 generalize across stacks; checks 5-7 PBIR-specific and skip silently for non-PBIR inputs.
3. **Tier 1 linter scope** — RESOLVED with full bidirectional fixture coverage of all 7 checks (per architect `arch-5`), runtime-parsed enum source-of-truth (per `arch-2`), suppression mechanic for hand-tuned grids (per `linter-1`), and reworded agent-promise to match what the linter actually verifies (per `linter-1`).
4. **IBCS opt-in trigger logic** — RESOLVED with the three-tier precedence rule + grep-able activation breadcrumb + Sága log entry on tag-triggered activation + the `environment-context.md` schema defined in this PR (per `arch-4`, `sec-4`, `ibcs-1`).
5. **Tableau promotion breaking-change check** — RESOLVED with the patch-version bump + migration note + anti-drift Gate 50 (per `arch-6`, `additive-1`). The tableau plugin's `viz-*.md` files become thin pointers + Tableau-specific deltas only.
6. **In-loop linter + audit-gates compatibility** — RESOLVED with the single-executable-two-callers contract (per `arch-1`) + purity contract (per `sec-2`) + bidirectional fixtures (per `arch-5`).
7. **Security: WebFetch return-envelope injection** — RESOLVED as a v0.1.0 hard requirement (per `arch-7`, `sec-1`). New knowledge file `webfetch-return-envelope-hardening.md` + Gate 49 fixture + skill-level WebFetch contract.
8. **"Power BI Slop" naming** — RESOLVED with neutral public-facing description + community-term citation in the anti-pattern catalog header (per `naming-1`).

---

## 6. Out-of-scope for this plan

These are real concerns but not what the build-plan panel should review:

- The Tier 3 render-verification loop (deferred to v0.2.0 by design, with security pre-requisites declared in §2.7).
- The cross-page consistency / `design-tokens.json` pattern (deferred to v0.2.0). v0.1.0 limitation is stated explicitly in the agent description to prevent silent-regression-on-upgrade.
- The marketing-site / `ravenpower.net` integration (separate repo, separate effort).
- Any change to the existing `pbir-enhanced-reference.md`, `dax-category-name-mismatch-zero-scores.md`, or `sempy-fabric-reference.md` files (they're stable and the new agent cross-references them).
- The `frontend-design` skill from `superpowers:frontend-design` — that's third-party, lives outside this marketplace's design discipline.
- The cross-marketplace WebFetch-hardening generalization (every agent that WebFetches needs the contract from §2.1) — routed to `security-reviewer` as a follow-up; this PR ships the floor for the data-viz agent only.

---

## 7. Why this is worth the effort (with honest scoping)

The marketplace's value proposition is *the framework that makes the domain work good*. The visualization-design discipline is one of the most-cited gaps in AI-generated dashboards across the industry — and one of the *most embarrassing* failure modes (visuals overlap; charts mismatch the data; KPI tiles look generic). Closing it inside `ravenclaude-core` with verified canon + a runnable linter + community-cited anti-pattern catalog is exactly the kind of work that distinguishes the marketplace from copy-pasted prompt collections. It also gives `power-bi-engineer` and `dashboard-builder` a sharper, more defensible output contract than either has today.

**Honest effort breakdown (per devil's-advocate gap `scope-creep-1`):**

| Deliverable | Estimate | Notes |
|---|---|---|
| Agent file (`data-viz-designer.md`) | 1.5h | Verbatim WCAG SCs, IBCS SUCCESS rules, FT 9 categories, Power BI Copilot limitations, contoso-examples grid math, dispatch table, invocation model, WebFetch contract |
| 4 skills (chart-from-intent, pbir-layout-engine, wcag-viz-contrast, ibcs-variance-reports) | 3h | Each with mermaid decision trees + stack-dispatch logic + grep-able activation breadcrumbs (IBCS) |
| 4 knowledge files (decision-trees, slop-catalog, webfetch-hardening, lint-doc) | 3h | 16-row anti-pattern catalog is the heaviest |
| Tier 1 linter + 12 fixtures + purity contract | 2h | Single executable; runtime enum parse; 7-check fixtures bidirectional; suppression mechanic; poisoned-body fixture |
| Gates 48-51 wiring in `scripts/audit-gates.sh` | 1h | Linter + WebFetch + tableau-anti-drift + schema-enum-drift |
| Tableau promotion (4 best-practices + 2 decision trees, thin-pointer pattern) | 2h | Plus migration note authoring |
| Cross-links + version bumps + prettier sweep + `.repo-layout.json` update | 1h | 4 plugins + marketplace.json |
| **Subtotal** | **13.5h** | |
| **1.5× contingency factor** | **20h** | Honest upper bound; do not pad further |

**Cut-list if budget overruns** (in order of cut-first):
1. The 4 Tableau promotions defer to a follow-up PR — they are not load-bearing for the agent's v0.1.0 promise. The anti-drift Gate 50 defers with them. Saves ~2.5h.
2. The IBCS skill defers to v0.1.1 once the trigger logic gets one more round of stress-testing. Saves ~1h (skill scaffolding) + reduces fixture count. The opt-in design means deferring doesn't break any v0.1.0 contract.
3. The webfetch-hardening fixture (Gate 49) could ship after the floor lands, but the contract itself ships in v0.1.0 regardless. Saves ~0.5h.

The cost is one focused PR — net additive within `ravenclaude-core`; one patch bump in `tableau` with a migration note; cross-link bumps in `power-platform` and `data-platform`. After the build-plan panel review confirms the tactical structure.

---

## 8. Open questions for the build-plan panel

P0/P1 strategic questions from v1 are RESOLVED inline above. The questions that remain are tactical and route to the build-plan / Panel 2 review:

1. **Build sequencing** — does the linter ship first (so subsequent skills can call it) or do the skills ship first (so the linter has a documented caller)?
2. **Tableau migration note copy** — exact wording of the consumer-facing note in tableau's release notes. Build plan should propose final text.
3. **`environment-context.md` schema formalization** — this PR ships the `finance_context` key. Are there other keys that should be defined in the same PR for cohesion, or does that bloat scope?
4. **`audit-gates.sh` gate numbering** — Gates 48-51 reserved here. Confirm no collision with concurrently-merging PRs.
5. **Cross-marketplace WebFetch-hardening follow-up** — when does that ship? Build plan should propose a deadline so the floor doesn't sit only here forever.
6. **Routing to Ultraplan vs local execution** — the build plan's routing-recommendation section (mandatory) answers this; Matt confirms before either path proceeds.
