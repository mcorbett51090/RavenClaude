# Phases 2–7 — Ultraplan delta-brief (data-viz-designer)

**Read this alongside [`build-plan.md`](./build-plan.md) and [`strategic-plan.md`](./strategic-plan.md).** The build plan is still the authoritative spec for Phases 2–7; this file records what has **changed in the repo since 2026-06-02** so an Ultraplan run doesn't execute against stale assumptions. Written 2026-06-04 after Phase 0 + Phase 1 shipped and `main` advanced.

**Routing (resolved):** strategic-plan §8 Q6 + the build-plan routing section both land on **`lean_ultraplan`**. Phase 0+1 (the deterministic linter — the testable, low-citation core) shipped locally; **Phases 2–7 (the agent + 4 skills + 3 knowledge files + 4 best-practice promotions + cross-links, ~13h, citation-heavy) are the Ultraplan job.** Do not local-author them in a depleted session — that manufactures the "Power BI Slop" this agent exists to prevent.

---

## 1. Already shipped — do NOT rebuild (merged in PR #271, ravenclaude-core v0.116.0)

| Build-plan item | Shipped as | Note |
|---|---|---|
| Phase 1 linter (`lint.py`, 7 checks) | `plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py` | stdlib-only; the one sanctioned cross-plugin read of `pbir-enhanced-reference.md` §1 is in its docstring |
| Phase 3.2 `pbir-layout-engine/SKILL.md` | shipped (pulled forward to complete the skill dir) | a counted skill; see §4 count discipline |
| Phase 1.5 — 12 fixtures | `tests/fixtures/data-viz/*.json` | each bad-page fires exactly its target check; warning checks (3/4/6) asserted under `--strict` |
| Phase 1.6 companion doc | `plugins/ravenclaude-core/knowledge/pbir-design-lint.md` | |
| Phase 2 linter gate (plan's "Gate 48") | **Gate 92** in `scripts/audit-gates.sh` | per-gate runner + main sequence; bidirectional |
| `.repo-layout.json` globs | added `tests/fixtures/data-viz/**`, `plugins/*/skills/*/*.py` | |

So the Ultraplan run **starts at Phase 3** (chart-from-intent / wcag-viz-contrast / ibcs-variance-reports skills + knowledge files), Phase 4 (agent), Phase 5 (tableau promotion), Phase 6 (cross-links + version cascade). The linter + its gate are done.

## 2. Gate-number reconciliation (strategic-plan §8 Q4 — the collision happened)

The plan reserved Gates **48–52**. **All are now occupied** (48 = WebFetch sanitizer, 49 = Mímir, 50 = Phase-0 emit/scrub, 51 = shell-router; 90/91/92 = dispatch-evaluator + this linter). Reassign the remaining plan gates:

| Plan gate | Purpose | Action |
|---|---|---|
| Gate 48 (linter) | layout-arithmetic | **DONE — shipped as Gate 92.** |
| Gate 49 (WebFetch poisoned-body) | injection neutered | **Reconcile, don't duplicate.** A deterministic WebFetch return-envelope sanitizer **already exists as the real Gate 48** (`sanitize-webfetch-body.py`). The data-viz agent should consume that existing floor; only add a *new* gate if the agent introduces a distinct sanitization surface. |
| Gate 50 (tableau anti-drift) | thin-pointer >30-line overlap | **→ Gate 94** |
| Gate 51 (schema-enum drift) | `visualType` enum vs `lint.py` | **→ Gate 95** |
| Gate 52 (stack-enum drift) | `stack` enum across files | **→ Gate 96** |

Update every build-plan reference to 49/50/51/52 accordingly. **Refreshed 2026-06-04 (evening): Gate 93 is now occupied too** (Learn-tab stepper render, `scripts/check-stepper-render.mjs`) — next free numbers are **94–96** (also free: 39, 52–59, 61–69, 71–79, 81–89 — but the recent convention uses the 90s band). **Re-verify the next-free-gate number against `scripts/audit-gates.sh` at run start (G-PRE-2 re-run) — it has drifted twice in one day.**

## 3. Phase 5 tableau promotion — source filenames are STALE

The plan (Phase 5.1–5.4) promotes `chart-type-follows-the-question.md`, `axis-integrity.md`, `color-and-accessibility.md`, `interactivity-intent-taxonomy.md` from `plugins/tableau/best-practices/`. **Those files do not exist under those names.** The actual files are `calc-*` / `data-*` / `embed-*` (e.g. `calc-aggregate-vs-row-level.md`, `data-relationships-before-joins.md`, `embed-connected-apps-jwt-not-trusted-tickets.md`) + `plugins/tableau/knowledge/viz-calc-decision-trees.md`.

**Action:** before Phase 5, re-derive which tableau best-practices actually carry **domain-neutral viz canon** worth promoting to `ravenclaude-core/best-practices/` (chart-type / axis-integrity / color-accessibility / interactivity may live inside differently-named files, or may not exist yet and need authoring). Do not promote files that aren't there. Tableau is at **v0.2.1** (G-PRE-3 satisfied — no version scaffold needed; patch-bump on the promotion). Phase 5 is **cut-list item #1** (strategic-plan §7) — defer it if budget overruns; the agent's v0.1.0 promise doesn't depend on it.

## 4. Count / version / regen discipline (per added skill)

Core skill count is now **35** (refreshed 2026-06-04 evening; was 34 when this brief was first written — **re-count `ls plugins/ravenclaude-core/skills/ | wc -l` at run start**, it moves). Each new skill the run adds (chart-from-intent, wcag-viz-contrast, ibcs-variance-reports) bumps:
- the `"N skills"` string in `plugins/ravenclaude-core/.claude-plugin/plugin.json` **and** `.claude-plugin/marketplace.json` (×2: metadata.description + the core plugin entry),
- the **must-fail fixture literal** in `scripts/audit-gates.sh` (currently `s.replace('35 skills','20 skills',1)` at `audit-gates.sh:477`) — keep it matching the real count or the marketplace-claims meta-test loses its teeth (the PR #247 lesson),
- ravenclaude-core `version` (minor, from **v0.120.0** as of this refresh — read the current value at run start) + regen `dashboard.html` / `repo-guide.html` / `copilot/` (Gates 11/13 + copilot freshness).

Per the plan, batch the version bump + regen at **Phase 6** (one cascade), not per-skill.

## 5. Citations — re-verify ALL of C1–C25 at use (the anti-slop core)

The citation table is dated **2026-06-02**; one entry has **already drifted** by 2026-06-04 (Opus 4.7 → Anthropic Legacy; 4.8 is the current top model — found this session). Before any citation is written into a consumer-facing knowledge/skill file, re-verify against its primary source and update the `[verified]` / `[unverified]` marker + date. Priority re-checks: WCAG 2.2 SC 1.4.3/1.4.11 (C1/C2), IBCS SUCCESS wording (C4), FT Visual Vocabulary 9 categories + last-commit (C7/C8), Power BI Copilot "no styling/formatting" + Q&A retirement date (C9/C12), contoso grid 24/16/312 measurements (C14), community-repo stars/licenses (C18–C21). DOIs (C15–C17) are stable. The `[unverified]` markers (C6 IBCS hex, C8 FT last-commit) MUST persist inline in the shipped files (G-CITE-1/2).

## 6. Open questions still needing Matt (strategic-plan §8)

Resolved by reality: Q1 (sequencing — linter shipped first ✓), Q4 (gate numbering — see §2), Q6 (routing — Ultraplan ✓). **Still open for the run / Matt:**
- **Q2** — exact tableau consumer-facing migration-note wording (only if Phase 5 is in scope).
- **Q3** — `environment-context.md` schema: this PR adds `finance_context: ibcs|none` (Phase 3.4); decide whether other keys join in the same PR or that bloats scope. (`environment-discovery` skill exists — G-PRE-1 ✓ — so the IBCS auto-trigger path is viable.)
- **Q5** — deadline for the cross-marketplace WebFetch-hardening follow-up so the floor doesn't live only here.
- Plus the design choices the build-plan TODO markers defer (IBCS auto-trigger vs explicit-only; the `stack` enum surface as a YAML preamble).

## 7. Pre-build gate dispositions verified this session (2026-06-04)

- **G-PRE-1** (environment-discovery skill) — ✓ present.
- **G-PRE-3** (tableau version) — ✓ v0.2.1.
- **G-PRE-5** (`pbir-enhanced-reference.md` §1 enum) — ✓ present; `lint.py` parses 35 `visualType` strings at runtime.
- **G-PRE-2** (next free gate) — resolved: 93–95 (see §2).
- **G-PRE-4 / G-PRE-6 / G-PRE-7 / G-PRE-8** — for the run: re-run the layout snippet for new paths; the `stack`-enum-single-source check (G-PRE-6) and the `_lintConfig` sidecar probe (G-PRE-7) only matter once the agent + skills exist; G-PRE-8 (rebase onto current `main` first) is mandatory — `main` moved three times during this session alone.
