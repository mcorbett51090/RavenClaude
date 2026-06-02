# Build Plan — `data-viz-designer` agent for RavenClaude

> **Status:** v1 awaiting Matt's approval, 2026-06-02. Tactical companion to [`strategic-plan.md`](./strategic-plan.md) v2. This document is the executable answer to "how do we ship v0.1.0?" — every load-bearing claim cites a primary source or carries a gate; every phase has acceptance tests; every new public surface has a typed contract.
>
> **Owner:** Matt Corbett (PR-merge authority + cut-list decision authority).

---

## Routing recommendation (advisory)

> The two-panel-plan-review workflow analyzed this plan against three signals (size/scope, web-research need, privacy) before convening the panels. This is ADVISORY: the panels ran locally; the recommendation is information for Matt to weigh before committing engineering effort.

**Verdict:** `lean_ultraplan` (confidence 0.72)
**One-line:** Lean Ultraplan — substantial multi-plugin build with verified citations already in hand, no privacy block, and the plan is ready to execute end-to-end to a PR.

**Signals:**
- **Size/scope:** favors *ultraplan* — Substantial multi-plugin build: 1 new agent + 4 skills + 3 knowledge files + 4 promoted best-practices + cross-links across 4 plugins (ravenclaude-core, power-platform, data-platform, tableau) + runnable Python linter with audit-gates fixtures (Gate 48) + version bumps in 3-4 plugins. Estimated 4-6 hours focused authoring — exactly the multi-file, cross-plugin shape Ultraplan handles well end-to-end with a PR landing on origin.
- **Web research need:** favors *local* — Two parallel deep-research streams plus a focused verification pass have already run — the strategic plan encodes verified specifics inline (WCAG 2.2 SCs verbatim, FT Visual Vocabulary 9 categories, IBCS SUCCESS rules with corrected wording, Power BI Copilot 2026 limitations verbatim, contoso-examples grid measurements, DOIs for Cleveland-McGill replications, community-skill star counts and licenses). The plan is rooted in repo state + already-verified citations with primary-source URLs. Minimal need for fresh web research during review.
- **Privacy:** favors *neutral* — Plan is entirely about domain-neutral open-source canon (Tufte, Cleveland-McGill, FT Visual Vocabulary, WCAG, IBCS, ColorBrewer) + public community repos (data-goblin, lukasreese, wardawg, MinaSaad1) + RavenClaude marketplace internals. No client names, no partner-confidential content, no credentials, no specific customer engagements. The marketplace itself is private-by-default but the plan content is publishable canon.

**Rationale:** The size/scope signal strongly favors Ultraplan: this is a 1-agent + 4-skills + 3-knowledge-files + 4-promotions + cross-links + runnable linter + audit-gates fixtures build spanning four plugins with three version bumps — substantially heavier than what local two-panel review is optimized for. Web research is already done (two research streams + verification pass with primary-source URLs embedded), so Ultraplan's cloud-research advantage is moot — but that doesn't argue against it, it just neutralizes one Ultraplan advantage. Privacy is neutral (domain-neutral canon, no client/partner content). The plan also explicitly states Matt wants this executed, not just reviewed ("after the panel review confirms the structure"), and Ultraplan lands a PR on origin which matches the documented Ultraplan workflow. Confidence 0.72 — not "use_local" because the build is genuinely substantial, not "consider_ultraplan" because two of three signals favor Ultraplan with no privacy block, but not higher because the heavy pre-verification means local review could competently stress-test the 8 open questions without losing much.

> If the verdict is `lean_ultraplan` or `consider_ultraplan` and Matt decides to route this plan to Ultraplan instead of executing locally, decline `ExitPlanMode` with a "sending to Ultraplan" note — the harness opens the browser session.

---

## Citations table

<!-- TODO(P1-2): Replace each "Primary source" cell with the exact fully-qualified URL (e.g. https://www.w3.org/TR/WCAG22/#contrast-minimum, https://doi.org/10.1145/1753326.1753357, https://github.com/Financial-Times/chart-doctor/tree/<sha>/visual-vocabulary); for repo-internal citations (C22, C23, C24), use the `file:line` form per AGENTS.md accuracy discipline; add a "Quoted excerpt" column with the exact string to grep for after re-fetching — this is what makes G-CITE-1/2 verifiable rather than honor-system — disposition: in parallel with Phase 4 execution (agent authoring is when citations get re-touched) -->

Every load-bearing technical claim either has a cited primary source verified this session OR carries an `[unverified]` marker AND a gate that settles it.

| # | Claim | Primary source | Verified | Marker | Gate that settles it |
|---|---|---|---|---|---|
| C1 | WCAG 2.2 SC 1.4.3 = 4.5:1 normal text contrast (verbatim quote) | w3.org/TR/WCAG22/ | 2026-06-02 | verified | Knowledge-freshness contract re-verifies every 90 days |
| C2 | WCAG 2.2 SC 1.4.11 = 3:1 for "parts of graphics required to understand the content" | w3.org/TR/WCAG22/ | 2026-06-02 | verified | Same |
| C3 | ColorBrewer authors = Cynthia Brewer + Mark Harrower + The Pennsylvania State University | colorbrewer2.org | 2026-06-02 | verified | Same |
| C4 | IBCS SUCCESS = SAY/UNIFY/CONDENSE/CHECK/EXPRESS/SIMPLIFY/STRUCTURE (corrected from "apply consistently") | ibcs.com/standards | 2026-06-02 | verified | Same; one `<system-reminder>` injection in body — neutered per Gate 49 |
| C5 | IBCS notation: actual=solid-black, PY=solid-medium-gray, plan=outlined, forecast=hatched | ibcs.com/standards | 2026-06-02 | verified (qualitative) | Same |
| C6 | IBCS hex codes `#0C3549`/`#CCCCCC`/`#44C088`/`#ED7373` | lukasreese/powerbi-claude-skills (third-party) | 2026-06-02 | `[unverified — third-party convention, IBCS PDF behind paywall]` | Build-plan gate G-CITE-1 confirms marker is present in agent file |
| C7 | FT Visual Vocabulary = 9 categories (Deviation/Correlation/Ranking/Distribution/Change over Time/Magnitude/Part-to-whole/Flow/Spatial) | github.com/Financial-Times/chart-doctor | 2026-06-02 | verified | Knowledge-freshness contract; one `<system-reminder>` injection on FT GitHub tree — neutered per Gate 49 |
| C8 | FT Visual Vocabulary last-commit date | github.com/Financial-Times/chart-doctor | unable | `[unverified — could not extract from GitHub HTML]` | G-CITE-2 confirms marker present |
| C9 | Power BI Copilot does NOT support "Styling or formatting changes" (verbatim) | learn.microsoft.com/en-us/power-bi/create-reports/copilot-create-reports (page date 2025-11-13) | 2026-06-02 | verified | Knowledge-freshness contract |
| C10 | Power BI canvas: 16:9 default; 1280×720 is smallest of four standard sizes | learn.microsoft.com/en-us/power-bi/create-reports/power-bi-report-display-settings (page date 2026-04-13) | 2026-06-02 | verified | Same |
| C11 | `displayOption` enum = `FitToPage`/`FitToWidth`/`ActualSize` (PascalCase) | Power BI JS SDK + PBIR Enhanced schema | 2026-06-02 | verified | Gate 51 (schema-enum drift) |
<!-- TODO(P1-7): Split C11 into C11a (JS SDK enum, with `powerbi-client` GitHub URL + commit SHA + filename:line) and C11b (PBIR Enhanced schema, with `pbir-enhanced-reference.md` file:line); declare which is authoritative for the agent's output contract and which is informational; if they ever diverge, name the disposition; Gate 51 currently watches drift between `pbir-enhanced-reference.md` and `lint.py` only — it does NOT watch drift against the JS SDK — disposition: in parallel with Phase 4 execution -->
| C12 | Q&A visual full retirement = December 2026 | Power BI Updates Blog "Deprecating Power BI Q&A" | 2026-06-02 | verified | Knowledge-freshness contract |
| C13 | Reports - Export To File In Group = 202 Accepted → poll GetExportToFileStatus → GET from resourceLocation | learn.microsoft.com/en-us/rest/api/power-bi/reports/export-to-file-in-group | 2026-06-02 | verified | Deferred to v0.2.0 with security pre-requisites |
| C14 | contoso-examples Overview horizontal grid: 24px margin + 16px gutter + 312px stride | github.com/bernatagulloesbrina/contoso-examples (7 of 9 visual.json) | 2026-06-02 | verified | `hand-tuned-vertical-grid-passes.json` fixture (Gate 48) |
<!-- TODO(P1-8): Expand C14 to specify (a) the commit SHA pinned at `github.com/bernatagulloesbrina/contoso-examples`, (b) the exact JSON path measured (e.g. `report/pages/<page>/visuals/<id>/visual.json#position.x`), (c) the 7 included file paths, (d) the 2 excluded file paths with exclusion rationale; add a fixture-derivation note in Phase 1.5 that names the SHA — the 24/16/312 values become hard-coded into the fixture and default tolerances, so unrecoverable measurements without a pinned SHA are a slow-leak failure mode — disposition: in parallel with Phase 1.5 execution -->
| C15 | Heer & Bostock 2010 DOI 10.1145/1753326.1753357 | doi.org | 2026-06-02 | verified | Stable academic record |
| C16 | Saket/Endert/Demiralp 2018 DOI 10.1109/TVCG.2018.2829750 | doi.org | 2026-06-02 | verified | Same |
| C17 | Bateman et al. 2010 DOI 10.1145/1753326.1753716 | doi.org | 2026-06-02 | verified | Same |
| C18 | data-goblin "Power BI Slop" coinage + 663⭐ + GPL-3.0 | github.com/data-goblin/power-bi-agentic-development | 2026-06-02 | verified | G-CITE-3 confirms commit SHA pinned in catalog |
| C19 | wardawg `pbir-report-workflow` 10-step "measure scaffold first" | github.com/wardawgmalvicious/claude-config | 2026-06-02 | verified | Same |
| C20 | MinaSaad1/pbi-cli 344⭐ MIT | github.com/MinaSaad1/pbi-cli | 2026-06-02 | verified | Same |
| C21 | microsoft/Analysis-Services/BestPracticeRules = 71 rules, 0 about visual layout | github.com/microsoft/Analysis-Services | 2026-06-02 | verified | Same |
| C22 | PBIR Enhanced schema version = `visualContainer/2.7.0` | `plugins/power-platform/knowledge/pbir-enhanced-reference.md` § 1 | repo state | verified | Gate 51 (schema-enum drift; pinned constant) |
| C23 | `visualType` enum (35+ strings) | `plugins/power-platform/knowledge/pbir-enhanced-reference.md` § 1 | repo state | verified | Gate 51 runtime parse |
| C24 | `environment-discovery` skill exists in ravenclaude-core | repo MEMORY + `plugins/ravenclaude-core/skills/environment-discovery/` | repo state | verified | G-PRE-1 (pre-build gate) |
| C25 | `audit-gates.sh` Gate 48 reserved (47 = latest in main) | `scripts/audit-gates.sh` | repo state | unverified — assumed | G-PRE-2 (pre-build gate confirms next free gate number) |
<!-- TODO(P1-9): Run G-PRE-2 as Step 0 of Phase 0 (BEFORE any other gate) and paste its output into the PR description; if Gates 48-51 are NOT free, the build plan must specify the find-and-replace target list explicitly — strategic plan §4, every Phase-2 task row, every Cross-cutting close-out row, every gap-debug table row mentioning Gate 49 or 51, the Citations table "Gate that settles it" column for C4/C7/C11; without a named replacement list, this is a silent-failure mode — disposition: in parallel with Phase 0 execution -->

---

## Pre-build gates

Open questions in the strategic plan settle via these gates BEFORE Phase 1 begins. Each gate has (a) the gate, (b) the pass criterion, (c) the disposition if it fails.

### G-PRE-1 — `environment-discovery` skill exists and reads `.ravenclaude/environment-context.md`

<!-- TODO(P1-3): Add a Phase 0 task whose acceptance test is "Document which G-PRE-1 disposition path was taken and confirm all downstream tasks reflect that choice"; if the skill is absent, add an explicit line to Phase 3.4's acceptance test "IBCS auto-trigger removed; SKILL.md documents explicit-only mode"; name that conditional as a RAID Issue if the gate fails — disposition: in parallel with Phase 0 execution -->

| | |
|---|---|
| **Gate** | `test -f plugins/ravenclaude-core/skills/environment-discovery/SKILL.md && grep -l 'environment-context.md' plugins/ravenclaude-core/skills/environment-discovery/` |
| **Pass** | Both checks return non-empty |
| **Fail disposition** | Add `environment-context.md` schema definition to ravenclaude-core in this PR (defines `finance_context: ibcs|none` key, default `none`) — adds ~0.5h to Phase 5. If skill itself doesn't exist, defer the auto-trigger path and ship IBCS as explicit-user-request-only in v0.1.0. |

### G-PRE-2 — Next free `audit-gates.sh` gate number

| | |
|---|---|
| **Gate** | `grep -oE 'Gate [0-9]+' scripts/audit-gates.sh \| sort -u -V \| tail -1` |
| **Pass** | Highest gate < 48 (Gates 48-51 are free) |
| **Fail disposition** | If 48-51 are taken, shift this PR's gates to next four free numbers and update strategic plan §4 + every reference in this build plan to match. |

### G-PRE-3 — `tableau` plugin version baseline

| | |
|---|---|
| **Gate** | `python3 -c "import json; print(json.load(open('plugins/tableau/.claude-plugin/plugin.json'))['version'])"` |
| **Pass** | Returns a semver string |
| **Fail disposition** | Tableau plugin lacks version field — fix in this PR with a starting `0.1.0`, then patch-bump to `0.1.1` per strategic plan §2.6. |

### G-PRE-4 — `.repo-layout.json` allows new paths

| | |
|---|---|
| **Gate** | Run the AGENTS.md verification snippet against a dry-run file list of every new path in this PR |
| **Pass** | "Layout OK — every new file matches at least one allowed glob." |
| **Fail disposition** | Update `.repo-layout.json` `allowed_globs` to include `plugins/*/skills/*/*.py`, `plugins/*/knowledge/*.py`, and `tests/fixtures/data-viz/**` in Phase 0 — before writing any file. |

### G-PRE-5 — `pbir-enhanced-reference.md` § 1 has parseable enum lists

| | |
|---|---|
| **Gate** | `python3 -c "import re; t=open('plugins/power-platform/knowledge/pbir-enhanced-reference.md').read(); m=re.search(r'## 1\\..*?(?=## 2\\.)', t, re.DOTALL); assert m and 'visualType' in m.group(0)"` |
| **Pass** | `§ 1` exists and references `visualType` |
| **Fail disposition** | Either fall back to hand-extracted enum constants in `lint.py` (with prominent TODO + Gate 51 still verifies divergence) OR update `pbir-enhanced-reference.md` § 1 in this PR with a machine-parseable enum block. Choose the latter; adds ~0.25h. |

### G-PRE-6 — `stack` enum drift across the 4 files

| | |
|---|---|
| **Gate** | Diff the `stack` enum list (`pbir\|tremor\|recharts\|evidence\|superset\|metabase`) across (a) `plugins/ravenclaude-core/agents/data-viz-designer.md` § Invocation contract, (b) `plugins/power-platform/agents/power-bi-engineer.md` cross-link, (c) `plugins/data-platform/agents/dashboard-builder.md` cross-link, (d) the four skill SKILL.md files. |
| **Pass** | Only the agent file contains the literal enum; the other three reference it via anchor. |
| **Fail disposition** | Fix the divergent file(s) to use the anchor reference. |

### G-PRE-7 — `_lintConfig` / `_lintIgnore` sidecar fallback (stub from P1-10)

<!-- TODO(P1-10): Verify that pbi-tools / pbicli / Power BI Desktop tolerate unknown root-level keys with a `_` prefix in page.json; if not, switch to a sidecar contract `<page>.lintconfig.json` colocated with page.json (same schema, linter loads it if present); document sidecar path in § Schemas / contracts as fallback; Phase 1.4 linter should support BOTH sources (sidecar preferred, in-line tolerated) for forward-compat — disposition: in parallel with Phase 1.4 execution -->

| | |
|---|---|
| **Gate** | Verify that pbi-tools / pbicli / Power BI Desktop tolerate unknown root-level keys with a `_` prefix in `page.json` (probe one well-formed `page.json` with a `_lintConfig` block through each tool's load/round-trip). |
| **Pass** | All three tools round-trip the `_*` keys unchanged (or ignore them silently); no rejection on load or save. |
| **Fail disposition** | Switch to sidecar contract: `<page>.lintconfig.json` colocated with `page.json`, same schema; linter loads sidecar if present, falls back to in-line `_lintConfig` only when sidecar is absent. Update § Schemas / contracts to document the sidecar path. Add a Phase 1.4 task to implement BOTH paths so the contract is forward-compatible. |

### G-PRE-8 — No concurrent PR is touching `.repo-layout.json`, `audit-gates.sh`, or `marketplace.json`

| | |
|---|---|
| **Gate** | `git fetch origin && git log origin/main --since='1 day ago' -- .repo-layout.json scripts/audit-gates.sh .claude-plugin/marketplace.json` |
| **Pass** | No log entries OR all log entries match the current branch's recent commits |
| **Fail disposition** | Rebase onto origin/main BEFORE proceeding; re-run G-PRE-2 and G-PRE-4 against the new base. |

---

## Phase-by-phase task tree

<!-- TODO(P1-1): Add a "depends on" column to each phase task table, or a short prose note per phase, calling out which tasks within a phase can parallelize vs. which are serial; at minimum, surface the critical path Phase 0 → Phase 1 (linter) → Phase 3.2 (SKILL.md pointing at linter) → Phase 4.1 (agent) → Phase 6.1/6.3 (cross-links); everything else is parallelizable once its inputs exist — disposition: in parallel with Phase 0 execution -->

Phases are sequenced so each builds on the prior. Within each phase, tasks are numbered. Effort estimates are honest; the order-of-magnitude scale is **quarter-day (~2h) / half-day (~4h) / day (~8h) / multi-day (>8h)**.

### Phase 0 — Pre-build hygiene (quarter-day)

| # | Task | Files touched | Composes | Acceptance test | Gate | Effort |
|---|---|---|---|---|---|---|
| 0.1 | Run all G-PRE-* gates | none | n/a | All gates pass or have a documented disposition | G-PRE-1 through G-PRE-8 | 0.25h |
| 0.2 | Update `.repo-layout.json` `allowed_globs` | `.repo-layout.json` | n/a | `python3 -m json.tool .repo-layout.json` clean; G-PRE-4 passes | G-PRE-4 re-run | 0.25h |
| 0.3 | Reserve Gates 48-51 in `scripts/audit-gates.sh` skeleton | `scripts/audit-gates.sh` | existing audit-gates framework | `bash -n scripts/audit-gates.sh` clean | Smoke run with `--list-gates` shows 48-51 reserved | 0.25h |
| 0.4 | (Conditional on G-PRE-3) Add `version` to `plugins/tableau/.claude-plugin/plugin.json` if missing | `plugins/tableau/.claude-plugin/plugin.json` | n/a | `python3 -m json.tool` clean; version is semver | G-PRE-3 re-run | 0.25h |

**Phase 0 total: ~1h.**

### Phase 1 — Linter + fixtures (quarter-day to half-day)

#### Table A — Linter Check Definitions

| Check ID | Name | Function | Applies to | Default severity |
|---|---|---|---|---|
| `check-1` | No-overlap (AABB) | `check_no_overlap(visuals)` | All stacks | error |
| `check-2` | Within-canvas | `check_within_canvas(visuals, page_w, page_h)` | All stacks | error |
| `check-3` | Equal-gap (horizontal) | `check_equal_gap(visuals, tolerance)` | All stacks | warning |
| `check-4` | Column-alignment (vertical) | `check_column_alignment(visuals, tolerance)` | All stacks | warning |
| `check-5` | No-empty-binding | `check_query_state(visual)` | PBIR only | error |
| `check-6` | Theme-compliance (count) | `check_theme_overrides(visual, max_n=N)` | PBIR only | warning |
| `check-7` | Schema-valid | `check_schema(visual, pinned_schema)` | PBIR only | error |

| # | Task | Files touched | Composes | Acceptance test | Gate | Effort |
|---|---|---|---|---|---|---|
| 1.1 | Write canonical `lint.py` with 7 checks + purity contract docstring (docstring MUST explicitly document the cross-plugin runtime read of `plugins/power-platform/knowledge/pbir-enhanced-reference.md` § 1 — this is the only sanctioned cross-plugin filesystem dependency in the linter) | `plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py` | `plugins/power-platform/knowledge/pbir-enhanced-reference.md` § 1 enum parse | `python3 -c "import ast; ast.parse(open('.../lint.py').read())"` clean; runs against `--help`; `grep 'plugins/power-platform/knowledge/pbir-enhanced-reference.md' plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py` returns at least one hit inside the module docstring | G-PRE-5 satisfied | 1h |
| 1.2 | Implement `layout_arithmetic_checks(visuals: list[dict]) -> list[Finding]` stack-agnostic core | same file | n/a | Unit test: 4 visuals on a 1280×720 page, no overlap → `[]`; same with overlap → 1 Finding | inline pytest at file bottom | 0.5h |
| 1.3 | Implement PBIR-specific checks (5, 6, 7) gated behind `--pbir` flag + auto-detect from `$schema` | same file | C22, C23 | Unit test: non-PBIR JSON skips checks 5-7 with info line | inline pytest | 0.5h |
| 1.4 | Implement `_lintConfig` + `_lintIgnore` suppression mechanic | same file | n/a | Unit test: vertical hand-tuned grid with `_lintConfig.tolerance.column_align_px: 999` passes check 4 | `hand-tuned-vertical-grid-passes.json` fixture | 0.25h |
| 1.5 | Write 12 fixtures under `tests/fixtures/data-viz/` | 12 JSON files | n/a | Each bad fixture fails exactly the targeted check; good fixture passes all 7 | run lint.py against each | 0.75h |
| 1.6 | Write `pbir-design-lint.md` companion doc | `plugins/ravenclaude-core/knowledge/pbir-design-lint.md` | links to `skills/pbir-layout-engine/lint.py:1` | `prettier --check` clean | n/a | 0.5h |

#### Table B — Fixture Manifest (consumed by task 1.5)

| Filename | Targets check | Input shape | Expected Findings | Exit code |
|---|---|---|---|---|
| `tests/fixtures/data-viz/good-page.json` | all | 4 non-overlapping visuals, within canvas, equal gaps, aligned columns, all bindings populated, valid schema | `[]` | 0 |
| `tests/fixtures/data-viz/bad-page-overlap.json` | check-1 | 2 visuals with overlapping bounding boxes | exactly one Finding with `check_id=check-1` | 1 |
| `tests/fixtures/data-viz/bad-page-out-of-canvas.json` | check-2 | 1 visual extends past `page.width` | exactly one Finding with `check_id=check-2` | 1 |
| `tests/fixtures/data-viz/bad-page-unequal-gaps.json` | check-3 | 3 visuals in a row with gaps differing by >4px | exactly one Finding with `check_id=check-3` | 1 |
| `tests/fixtures/data-viz/bad-page-column-misaligned.json` | check-4 | 2 visuals in different rows with `x` values differing by >0 | exactly one Finding with `check_id=check-4` | 1 |
| `tests/fixtures/data-viz/bad-page-empty-bindings.json` | check-5 | 1 PBIR visual with empty `queryState.<role>.projections` | exactly one Finding with `check_id=check-5` | 1 |
| `tests/fixtures/data-viz/bad-page-theme-override-explosion.json` | check-6 | 1 PBIR visual with >N `objects` + `visualContainerObjects` entries | exactly one Finding with `check_id=check-6` | 1 |
| `tests/fixtures/data-viz/bad-page-bad-schema-unknown-visualType.json` | check-7 | 1 PBIR visual with `visualType` not in the runtime-parsed enum | exactly one Finding with `check_id=check-7` | 1 |
| `tests/fixtures/data-viz/bad-page-bad-schema-invalid-displayOption.json` | check-7 | 1 PBIR page with `displayOption` not in `{FitToPage, FitToWidth, ActualSize}` | exactly one Finding with `check_id=check-7` | 1 |
| `tests/fixtures/data-viz/hand-tuned-vertical-grid-passes.json` | check-4 suppression | Verified contoso-examples Overview pattern: 4 KPIs on aligned columns, vertical rows at hand-tuned y values | `[]` (suppression-mechanic test) | 0 |
| `tests/fixtures/data-viz/poisoned-fetched-body.json` | n/a (Gate 49) | A fetched body with embedded `<system-reminder>` injection | n/a (Gate 49 asserts sanitized output) | n/a |
| `tests/fixtures/data-viz/enum-drift-divergence.json` | n/a (Gate 51) | Synthetic divergence between `pbir-enhanced-reference.md` enum and `lint.py` runtime parse | n/a (Gate 51 asserts drift detection) | n/a |

**Phase 1 total: ~3.5h.**

### Phase 2 — Audit-gates wiring (Gates 48-51) (quarter-day)

| # | Task | Files touched | Composes | Acceptance test | Gate | Effort |
|---|---|---|---|---|---|---|
| 2.1 | Add Gate 48 (linter bidirectional) to `scripts/audit-gates.sh` | `scripts/audit-gates.sh` | Phase 1 fixtures | Bad fixture exits non-zero; good fixture exits zero; smoke assertion "gate ran" present | `scripts/audit-gates.sh` runs Gate 48 | 0.5h |
| 2.2 | Add Gate 49 (WebFetch poisoned-body neutered) | same | `poisoned-fetched-body.json` fixture | Fixture's `<system-reminder>` content does NOT appear in agent output | same | 0.25h |
<!-- TODO(P1-5): Redesign Gate 49 to test a deterministic sanitizer layer instead of post-LLM observation; define `sanitize_webfetch_body(raw: str) -> str` in `lint.py` (or a shared util); place its tests in `tests/fixtures/test_pbir_lint.py`; have Gate 49 invoke that function against `poisoned-fetched-body.json` and assert injection strings are absent from the sanitized output; pair with a clean fixture (`clean-fetched-body.json`) for bidirectionality; document in `webfetch-return-envelope-hardening.md` that the sanitizer gate is the security floor, not post-LLM observation — disposition: in parallel with Phase 2.2 execution -->
| 2.3 | Add Gate 50 (tableau anti-drift; thin-pointer >30 lines of overlap fails) | same | normalized text-similarity helper | A bad fixture (tableau file regrown past 30 lines) fails; a good fixture (thin pointer) passes | same | 0.5h |
| 2.4 | Add Gate 51 (schema-enum drift between `plugins/power-platform/knowledge/pbir-enhanced-reference.md` § 1 and `lint.py` runtime parse) | same | `enum-drift-divergence.json` fixture | Fixture forces divergence and Gate 51 catches it | same | 0.25h |
| 2.5 | Add Gate 52 (runtime drift detector for the `stack` enum — matches Gate 51 pattern but for `stack` instead of `visualType`; diffs the agent's canonical enum vs. the strings appearing in `power-bi-engineer.md`, `dashboard-builder.md`, and the four skill SKILL.md files) | same | `stack-enum-drift-divergence.json` fixture (synthetic) | Fixture forces a divergent inline enum in a downstream file and Gate 52 catches it; clean fixture (all downstream files use anchor reference) passes | same | 0.25h |

**Phase 2 total: ~1.75h** (added 0.25h for Gate 52).

### Phase 3 — Skills + knowledge files (half-day)

| # | Task | Files touched | Composes | Acceptance test | Gate | Effort |
|---|---|---|---|---|---|---|
| 3.1 | Author `skills/chart-from-intent/SKILL.md` with FT 9-category mermaid tree + stack-dispatch contract | `plugins/ravenclaude-core/skills/chart-from-intent/SKILL.md` | C7, C18, agent stack contract (see [Invocation contract](#invocation-contract) for the canonical `stack` enum) | `prettier --check` clean; frontmatter passes `scripts/check-frontmatter.py` if applicable | n/a | 0.75h |
| 3.2 | Author `skills/pbir-layout-engine/SKILL.md` pointing at `lint.py` | `plugins/ravenclaude-core/skills/pbir-layout-engine/SKILL.md` | Phase 1 linter | Same | n/a | 0.5h |
| 3.3 | Author `skills/wcag-viz-contrast/SKILL.md` | `plugins/ravenclaude-core/skills/wcag-viz-contrast/SKILL.md` | C1, C2, C3 | Same | n/a | 0.5h |
| 3.4 | Author `skills/ibcs-variance-reports/SKILL.md` with precedence-resolved trigger + breadcrumb spec | `plugins/ravenclaude-core/skills/ibcs-variance-reports/SKILL.md` | C4, C5, C6 (with `[unverified]` marker), `environment-context.md` schema | Same; trigger-path fixture tests pass | n/a | 0.75h |

<!-- TODO(P1-4): Promote the `finance_context` template update to an unconditional task in Phase 3 (after task 3.4); the task: add `finance_context: ibcs | none  # default: none` to `plugins/ravenclaude-core/templates/environment-context.md` with an explanatory comment; acceptance test: `grep 'finance_context' plugins/ravenclaude-core/templates/environment-context.md`; G-PRE-1 currently passes (skill exists), so the existing G-PRE-1 fail-disposition-conditional update never fires — needs to be unconditional — disposition: in parallel with Phase 3.4 execution -->

<!-- TODO(P1-14): Add task 3.4a — create 3 small fixtures under `tests/fixtures/data-viz/ibcs/` (one per trigger path: `user_request`, `explicit_mention`, `finance_context_tag`); each fixture defines input conditions and asserts the breadcrumb regex matches; wire into pytest invocation in Phase 7 close-out; move the Gate column from `n/a` to the new test invocation — disposition: in parallel with Phase 3.4 execution -->

| 3.5 | Author `knowledge/visual-design-decision-trees.md` (5 mermaid trees) | `plugins/ravenclaude-core/knowledge/visual-design-decision-trees.md` | C7, C15, C16, C17, promoted Tableau trees | `prettier --check` clean | n/a | 0.75h |
| 3.6 | Author `knowledge/power-bi-slop-anti-patterns.md` (16-row catalog) | `plugins/ravenclaude-core/knowledge/power-bi-slop-anti-patterns.md` | C18-C21, header cites "Power BI Slop (Kurt Buhler, data-goblin)" once | Same; each row has detector + severity + fix + URL + verified-on date + commit SHA | G-CITE-3 | 1h |
| 3.7 | Author `knowledge/webfetch-return-envelope-hardening.md` | `plugins/ravenclaude-core/knowledge/webfetch-return-envelope-hardening.md` | Documents the two confirmed injection sites + the contract | Same | n/a | 0.25h |

**Phase 3 total: ~4.5h.**

### Phase 4 — Agent file (quarter-day)

| # | Task | Files touched | Composes | Acceptance test | Gate | Effort |
|---|---|---|---|---|---|---|
| 4.1 | Author `agents/data-viz-designer.md` | `plugins/ravenclaude-core/agents/data-viz-designer.md` | All Phase 3 skills + knowledge files; C1-C24 | `scripts/check-frontmatter.py` passes (`audience`, `works_with`, `scenarios`, `quickstart` schema); `prettier --check` clean | G-CITE-1, G-CITE-2 inspect for required `[unverified]` markers | 1.5h |
| 4.2 | Update `agents/designer.md` with the inverse dispatch table | `plugins/ravenclaude-core/agents/designer.md` | Strategic plan §2.1 dispatch table | `prettier --check` clean; routing-table rows match `data-viz-designer.md` | n/a | 0.25h |

**Phase 4 total: ~1.75h.**

### Phase 5 — Tableau promotion + thin-pointer rewrite (quarter-day to half-day)

| # | Task | Files touched | Composes | Acceptance test | Gate | Effort |
|---|---|---|---|---|---|---|
| 5.1 | Promote `chart-type-follows-the-question.md` core to `plugins/ravenclaude-core/best-practices/` | `plugins/ravenclaude-core/best-practices/chart-type-follows-the-question.md` | tableau source | `prettier --check` clean | n/a | 0.5h |
| 5.2 | Promote `axis-integrity.md` core | `plugins/ravenclaude-core/best-practices/axis-integrity.md` | tableau source | Same | n/a | 0.5h |
| 5.3 | Promote `color-and-accessibility.md` core | `plugins/ravenclaude-core/best-practices/color-and-accessibility.md` | tableau source | Same | n/a | 0.5h |
| 5.4 | Promote `interactivity-intent-taxonomy.md` core | `plugins/ravenclaude-core/best-practices/interactivity-intent-taxonomy.md` | tableau source | Same | n/a | 0.5h |
| 5.5 | Rewrite each tableau `viz-*.md` to thin pointer + Tableau-specific delta | 4 files in `plugins/tableau/best-practices/` | promoted core files | Each file ≤ 30 lines of overlap with its core counterpart; Gate 50 passes | Gate 50 | 0.75h |
| 5.6 | Promote 2 decision trees from `plugins/tableau/knowledge/viz-calc-decision-trees.md` to `visual-design-decision-trees.md` | both files | Phase 3.5 output | `prettier --check` clean; LOD/FIXED trees remain in tableau | n/a | 0.5h |
| 5.7 | Author tableau migration note in `plugins/tableau/CHANGELOG.md` (or release-notes equivalent) | `plugins/tableau/CHANGELOG.md` if extant; else inline in `plugins/tableau/CLAUDE.md` | Strategic plan §2.4 migration text | Migration note matches §2.4 verbatim | n/a | 0.25h |

**Phase 5 total: ~3.5h.** Cut-list candidate per strategic plan §7 if budget overruns.

### Phase 6 — Cross-links + version bumps (quarter-day)

| # | Task | Files touched | Composes | Acceptance test | Gate | Effort |
|---|---|---|---|---|---|---|
| 6.1 | Add knowledge prior to `plugins/power-platform/agents/power-bi-engineer.md` (cross-link to data-viz-designer; the prior MUST reference the canonical stack enum via anchor — see [Invocation contract](#invocation-contract) for the canonical `stack` enum — NOT restate the enum values) | one file | Phase 4 agent | `prettier --check` clean | n/a | 0.25h |
| 6.2 | Update `plugins/power-platform/CLAUDE.md` §8a knowledge-bank table | one file | n/a | Same | n/a | 0.25h |
| 6.3 | Add knowledge prior to `plugins/data-platform/agents/dashboard-builder.md` (cross-link to data-viz-designer; the prior MUST reference the canonical stack enum via anchor — see [Invocation contract](#invocation-contract) for the canonical `stack` enum — NOT restate the enum values) | one file | Phase 4 agent | Same | n/a | 0.25h |
| 6.4 | Update `plugins/data-platform/CLAUDE.md` §8a equivalent | one file | n/a | Same | n/a | 0.25h |
| 6.5 | Bump `plugins/ravenclaude-core/.claude-plugin/plugin.json` to 0.109.0 + matching `.claude-plugin/marketplace.json` entry | both files | n/a | `python3 -m json.tool` clean; CI version-drift check passes | Audit-gates manifest version-match | 0.25h |
| 6.6 | Bump `plugins/power-platform/.claude-plugin/plugin.json` to 0.21.1 + marketplace | both | n/a | Same | Same | 0.1h |
| 6.7 | Bump `plugins/data-platform/.claude-plugin/plugin.json` +0.0.1 + marketplace | both | n/a | Same | Same | 0.1h |
| 6.8 | Bump `plugins/tableau/.claude-plugin/plugin.json` +0.0.1 + marketplace | both | G-PRE-3 outcome | Same | Same | 0.1h |

**Phase 6 total: ~1.5h.**

### Phase 7 — Close-out (quarter-day)

| # | Task | Files touched | Composes | Acceptance test | Gate | Effort |
|---|---|---|---|---|---|---|
| 7.1 | `npx --yes prettier --write .` then `--check .` | every file with prettier-recognized extension | n/a | `prettier --check .` exits 0 | n/a | 0.25h |
| 7.2 | `scripts/audit-gates.sh` whole-run | none | Phase 0-6 | Exit 0 | All gates including 48-51 | 0.25h |
| 7.3 | AGENTS.md layout-allow-list verification snippet | none | Phase 0.2 | "Layout OK" | G-PRE-4 final | 0.1h |
| 7.4 | `scripts/check-checkout-fresh.sh` (advisory) | none | n/a | Warns or passes | n/a | 0.1h |
| 7.5 | JSON validity sweep (all plugin.json + marketplace.json + .repo-layout.json) | none | n/a | All `python3 -m json.tool` exit 0 | n/a | 0.1h |
| 7.6 | `bash -n` on `lint.py`-adjacent shell + executability check | none | Phase 1, 2 | Exit 0 | n/a | 0.1h |
| 7.7 | Open PR via GitHub MCP path (per CLAUDE.md remote-environment recipe) | none | All phases | PR exists with `draft: true` | n/a | 0.25h |

**Phase 7 total: ~1.25h.**

**Grand total: ~17h** (within the 20h-with-contingency budget from strategic plan §7). Cut-list per §7 if overrun.

---

## Schemas / contracts

Every new public surface gets its exact shape specified — type-level, not prose.

### Linter CLI

```text
python3 plugins/ravenclaude-core/skills/pbir-layout-engine/lint.py [OPTIONS] <input-path>

ARGUMENTS:
  input-path                Path to a single visual.json, a page directory containing
                            visual.json files, or a fixture directory containing both.
                            MUST NOT contain "..". MUST resolve inside the repo root.

OPTIONS:
  --pbir                    Force PBIR-specific checks (5, 6, 7). Default: auto-detect
                            from presence of `$schema` in input.
  --no-pbir                 Force off PBIR-specific checks. Useful for non-PBIR inputs.
  --format=text|json        Output format. Default: text.
  --strict                  Exit non-zero on any Finding of severity >= warning.
                            Default: exit non-zero only on severity == error.
  --tolerance-gap=PX        Override default ±4 for check 3. Per-page _lintConfig wins.
  --tolerance-align=PX      Override default 0 for check 4. Per-page _lintConfig wins.
  --list-checks             Print the 7 checks and exit.
  --version                 Print pinned schema version constant and exit.

EXIT CODES:
  0    All checks pass (or only info-level Findings).
  1    One or more Findings of error severity (or warning with --strict).
  2    I/O error, parse error, or argv path rejection (purity-contract failure).
  3    Schema-enum parse failure from `pbir-enhanced-reference.md` § 1.
```

<!-- TODO(P1-11): Reconcile § Linter CLI's input contract (single visual.json / page directory / fixture directory) with the `_lintConfig` schema example (which shows a top-level page.json with visuals[] inline) — these are currently mutually exclusive; either (a) linter walks `<page>/page.json` + `<page>/visuals/<id>/visual.json` files with `_lintConfig` on page.json and `_lintIgnore` on each visual.json, or (b) linter accepts a synthetic flattened `page-with-visuals.json` for fixture convenience and a real PBIR tree for production; state which and add directory-walking logic to Phase 1.1's acceptance test — disposition: in parallel with Phase 1.1 execution -->

**`--format=json` output envelope:**

```json
{
  "schema_version": "1.0.0",
  "linter_version": "<pinned constant in lint.py>",
  "input_path": "<resolved absolute path>",
  "exit_code": 0,
  "summary": {"info": 0, "warning": 0, "error": 0},
  "findings": [
    {"check_id": "check-1", "severity": "error", "page": "Overview", "visual_id": "kpi-1", "message": "...", "fix_hint": "..."}
  ]
}
```

**Encoding rules:**
- snake_case keys (match the `Finding` dataclass field names).
- `null` instead of key omission for unknown optional fields.
- `schema_version` is the contract version (semver), NOT the linter version.
- `exit_code` mirrors the process exit code (0 = pass, 1 = fail, 2 = parse error, 3 = I/O error).
- Gate 48 asserts both the exit code AND the JSON envelope shape (use `jq` for shape validation).

### `Finding` type (Python dataclass)

<!-- TODO(P1-16): Tighten `fix_hint` contract — single line, ≤200 chars, plain text (no markdown, no newlines, no code fences), imperative voice (e.g., "Move kpi-1 to x=24"); for multi-line guidance, link to the knowledge file from the message field; add a unit test in Phase 1.2 asserting `'\n' not in finding.fix_hint and len(finding.fix_hint) <= 200` across the fixture corpus — disposition: in parallel with Phase 1.2 execution -->

```python
from dataclasses import dataclass
from typing import Literal

Severity = Literal["info", "warning", "error"]
CheckId = Literal["check-1", "check-2", "check-3", "check-4",
                  "check-5", "check-6", "check-7"]

@dataclass(frozen=True)
class Finding:
    check_id: CheckId
    severity: Severity
    page: str             # Page name from page.json or path leaf
    visual_id: str | None # None for page-level findings (within-canvas check)
    message: str          # Human-readable description
    fix_hint: str         # One-line actionable suggestion
```

### `_lintConfig` block (per page.json)

```jsonc
{
  "page": "Overview",
  "width": 1280,
  "height": 720,
  "_lintConfig": {
    "tolerance": {
      "equal_gap_px": 4,        // default 4
      "column_align_px": 0      // default 0 (strict equality)
    }
  },
  "visuals": [
    {
      "id": "kpi-1",
      "position": {"x": 24, "y": 120, "width": 296, "height": 100},
      "_lintIgnore": ["check-3"]   // omit this visual from check 3
    }
  ]
}
```

### IBCS activation breadcrumb (skill output prefix)

```text
IBCS mode active — triggered by <user_request|explicit_mention|finance_context_tag>
```

Exact regex: `^IBCS mode active — triggered by (user_request|explicit_mention|finance_context_tag)$`

### `.ravenclaude/environment-context.md` `finance_context` key

```yaml
finance_context: ibcs | none   # default: none
```

When `ibcs`, the `ibcs-variance-reports` skill auto-activates UNLESS explicit user request overrides it.

### Sága log entry for tag-triggered IBCS activation

Path: `.ravenclaude/runs/data-viz/ibcs-activations/<YYYY-MM-DDTHH-MM-SS>.md`

Body:

```yaml
---
triggered_at: <ISO 8601>
trigger: finance_context_tag
context_file: .ravenclaude/environment-context.md
context_value: ibcs
calling_agent: <agent name>
calling_skill: ibcs-variance-reports
---

# IBCS activation breadcrumb

Auto-activated by finance_context tag (not by explicit user request or explicit IBCS mention).
```

<a id="invocation-contract"></a>

### `data-viz-designer` agent invocation contract

**This section is the SINGLE SOURCE OF TRUTH for the `stack` enum.** All other locations (Phase 3.1's chart-from-intent skill, Phase 6.1, Phase 6.3, the agent OUTPUT envelope) reference this section by anchor — they do NOT restate the enum values.

**`stack` is a YAML-preamble convention** — NOT a CLI flag. The calling agent (Team Lead) or a human composes a YAML preamble at the top of the data-viz-designer's prompt; the agent parses that preamble. There is no Python entry-point with argv. The Team Lead is responsible for composing the preamble correctly.

```text
ARGUMENTS (composed into a YAML preamble by Team Lead or calling specialist):
  intent              one of: deviation | correlation | ranking | distribution |
                              change_over_time | magnitude | part_to_whole | flow | spatial
  data_shape          free-form description of cardinality / dimensionality / temporality
  stack               one of: pbir | tremor | recharts | evidence | superset | metabase
                      OR absent — agent returns stack-agnostic design only
  ibcs                optional: yes | no | auto
                      yes: force IBCS on; no: force IBCS off; auto (default): apply precedence rules

OUTPUT (structured):
  ft_category         one of the 9 FT categories
  chart_family        e.g. "Diverging bar"
  cleveland_mcgill_rank   1-10 with citation
  layout_arithmetic   {page_w, page_h, margin, gap, n_cols, n_rows, computed positions}
  palette             {family, ColorBrewer ref, hex codes, colorblind_safe: bool}
  wcag_pass           {sc_1_4_3: bool, sc_1_4_6: bool, sc_1_4_11: bool}
  linter_report       Finding[] (must be empty for declared-done status)
  webfetch_notes      "N injection attempts in fetched bodies; treated as data" (if applicable)
  ibcs_mode           on | off (with breadcrumb if on)
  stack_warning       string|null  (see "Unknown stack value behavior" below)
```

**Unknown stack value behavior:** the agent emits `stack_warning: "unknown stack 'X'; returning stack-agnostic design"` in its output envelope and proceeds as if `stack` were absent.

<!-- TODO(P1-17): Replace CLI-style ARGUMENTS block with explicit YAML preamble template (intent / data_shape / stack / ibcs as YAML frontmatter delimited by ---); add parse contract that the YAML preamble is authoritative over conflicting prose, and prose-extracted values are marked `[inferred]` in the output envelope; update Phase 6.1 and Phase 6.3 to add the preamble template to consumer instructions — disposition: in parallel with Phase 4 execution -->

### Agent OUTPUT envelope (JSON Schema)

**Serialization:** the agent's structured output is emitted as a JSON object inside a fenced ```json block at the end of its transcript. Required fields, optional fields, and types are:

```json
{
  "schema_version": "1.0.0",
  "ft_category": "string (one of: deviation|correlation|ranking|distribution|change-over-time|magnitude|part-to-whole|flow|spatial)",
  "chart_family": "string (e.g., 'bar', 'line', 'scatter', 'pie', 'kpi')",
  "layout_arithmetic": {
    "page_w": "int (pixels)",
    "page_h": "int (pixels)",
    "margin": "int (pixels)",
    "gap": "int (pixels)",
    "n_cols": "int",
    "n_rows": "int",
    "positions": [
      {"visual_id": "string", "x": "int", "y": "int", "width": "int", "height": "int"}
    ]
  },
  "wcag_pass": {
    "sc_1_4_3_pass": "boolean",
    "sc_1_4_11_pass": "boolean",
    "lowest_contrast_ratio": "number"
  },
  "linter_report": [
    {"check_id": "string", "severity": "string (info|warning|error)", "page": "string|null", "visual_id": "string|null", "message": "string", "fix_hint": "string"}
  ],
  "ibcs_mode": "string (active|inactive|n/a)",
  "cleveland_mcgill_rank": {"rank": "int (1..10)", "citation_doi": "string"},
  "palette": {"family": "string (qualitative|sequential|diverging)", "colorbrewer_ref": "string", "hex_codes": "list[string]", "colorblind_safe": "boolean"},
  "webfetch_notes": "string",
  "stack_warning": "string|null"
}
```

**Required fields:** `ft_category`, `chart_family`, `layout_arithmetic`, `wcag_pass`, `linter_report`, `ibcs_mode`.
**Optional fields:** `cleveland_mcgill_rank`, `palette`, `webfetch_notes`, `stack_warning`.
**Unknown fields:** tolerated (forward-compat). Parsers MUST ignore unrecognized keys.
**Forbidden:** any key with a leading underscore (`_*` reserved for `_lintConfig`/`_lintIgnore` in PBIR JSON, not agent output).

`linter_report[]` is the JSON shape of the `Finding` dataclass (snake_case keys); same shape as `lint.py --format=json` emits.

<!-- TODO(P1-12): Specify environment-context.md parse contract for finance_context key — Markdown with YAML frontmatter delimited by `---`; skill reads frontmatter only (not the body); defaults `finance_context` to `none` if absent; treats unknown values as `none` with a one-line warning to agent transcript; add fixtures `environment-context-missing.md`, `environment-context-ibcs.md`, `environment-context-unknown.md` — disposition: in parallel with Phase 3.4 execution -->

---

## Rollout & rollback

### Enable (consumer side)

```text
# In any consumer Claude Code project:
/plugin marketplace update ravenclaude
/reload-plugins
```

The new agent + skills + knowledge files + best-practices appear automatically. Existing `power-bi-engineer` and `dashboard-builder` agents get the inline knowledge prior referencing `data-viz-designer`.

For Tableau-only consumers (no ravenclaude-core installed): a one-line pointer appears in the existing `viz-*.md` files referencing a file the consumer doesn't have. Degraded readability, not breakage. Documented in the tableau migration note.

### Disable (rollback — MUST NOT depend on the feature itself)

```text
# Option A — version-pin downgrade (cleanest):
/plugin install ravenclaude-core@ravenclaude --version=0.108.0
/plugin install power-platform@ravenclaude --version=0.21.0
/plugin install tableau@ravenclaude --version=<prior>
/reload-plugins

# Option B — disable via comfort-posture (no version downgrade required):
# Edit .ravenclaude/comfort-posture.yaml and set:
#   agents.data-viz-designer: disabled
# Then: /set-posture
# The Team Lead skips data-viz-designer; calls fall back to power-bi-engineer
# inline rules (which still ship in the prior k-prior block).

# Option C — emergency: revert the merge commit on origin/main and bump everyone
# to the prior version. Does NOT require the linter, skills, or agent to function.
```

The disable path uses standard plugin-version management + comfort-posture — neither depends on `data-viz-designer` or its skills working. If the linter or skills are completely broken, rollback still works.

---

## Telemetry & observability

| Where it logs | Path | What lands there |
|---|---|---|
| Linter Findings (per run) | `.ravenclaude/runs/data-viz/lint/<timestamp>.json` | All Findings + exit code + invocation argv |
| IBCS auto-activation (tag-triggered only) | `.ravenclaude/runs/data-viz/ibcs-activations/<timestamp>.md` | Breadcrumb + trigger source |
| WebFetch injection-detection | inline in agent transcript + `.ravenclaude/runs/data-viz/webfetch/<timestamp>.log` | URL + count of injection attempts neutered |
| Agent invocation (Team Lead spawn) | Sága log (standard) | structured output contract above |
| Audit-gates Gate 48-51 results | `.ravenclaude/runs/audit-gates/<timestamp>.json` | Per-gate pass/fail + duration |

### How to debug a failure

| Failure mode | First check | Then |
|---|---|---|
| Linter exits 2 (path rejection) | argv contains `..` or absolute path outside repo? | Re-invoke with a path inside the repo |
| Linter exits 3 (enum parse failure) | `pbir-enhanced-reference.md` § 1 changed shape? | Fix the reference file OR fix the parse regex in `lint.py`; Gate 51 catches drift |
| Linter false-positive on hand-tuned grid | `_lintConfig.tolerance.*` or `_lintIgnore` set? | Add suppression per the schema; verify against `hand-tuned-vertical-grid-passes.json` |
| IBCS activated unexpectedly | Check the breadcrumb in agent output | If `finance_context_tag`, edit `.ravenclaude/environment-context.md`; if `explicit_mention`, adjust the prompt |
| Dispatch ambiguity (`designer` vs `data-viz-designer`) | Check the inverse dispatch table in `designer.md` | Route per the 7-row table in `data-viz-designer.md` §2.1 |
| WebFetch injection silently passes | Gate 49 should have caught it | If Gate 49 is green but content slipped — log a defect; this is the security floor |

### Artifact locations summary

- **Linter:** `.ravenclaude/runs/data-viz/lint/`
- **IBCS activations:** `.ravenclaude/runs/data-viz/ibcs-activations/`
- **WebFetch hardening:** `.ravenclaude/runs/data-viz/webfetch/`
- **Audit-gates:** `.ravenclaude/runs/audit-gates/`

---

## Versioning + migration

| Plugin | Before | After | Type | Migration note (consumer-visible) |
|---|---|---|---|---|
| `ravenclaude-core` | 0.108.0 | 0.109.0 | minor (additive) | "New agent `data-viz-designer` + 4 skills + 4 knowledge files + 4 promoted best-practices. Non-breaking." |
| `power-platform` | 0.21.0 | 0.21.1 | patch | "`power-bi-engineer` now invokes `ravenclaude-core/agents/data-viz-designer` when work is dashboard/chart/KPI-shaped. Include `stack: pbir` in the YAML preamble when invoking (see the data-viz-designer Invocation contract for the canonical `stack` enum). Non-breaking." |
| `data-platform` | (current) | +0.0.1 | patch | "`dashboard-builder` now invokes `ravenclaude-core/agents/data-viz-designer` when work is dashboard/chart/KPI-shaped. Include a `stack:` field in the YAML preamble when invoking (see the data-viz-designer Invocation contract for the canonical `stack` enum). Non-breaking." |
| `tableau` | (current) | +0.0.1 | patch | "Canon-of-record for chart-type-follows-the-question, axis-integrity, color-and-accessibility, and interactivity-intent-taxonomy promoted to `ravenclaude-core/best-practices/`. The Tableau-specific deltas remain in `plugins/tableau/best-practices/viz-*.md` as thin pointers. **If you installed `tableau` without `ravenclaude-core`**, the `viz-*.md` files now reference a file you don't have for full canon — install `ravenclaude-core` to get it, or rely on the Tableau-specific deltas. No mechanical breakage." |

**What consumers see on `/plugin marketplace update`:**
- `ravenclaude-core` consumers: new agent + skills + knowledge appear in `/plugin` UI. No breakage.
- `power-platform` consumers: `power-bi-engineer` description updated; cross-link present. No breakage.
- `data-platform` consumers: `dashboard-builder` description updated; cross-link present. No breakage.
- `tableau`-only consumers: thin-pointer references appear in `viz-*.md` files; the referenced core files don't exist in their install. Mitigation: install `ravenclaude-core` (recommended), or rely on Tableau-specific deltas (sufficient for Tableau-specific work).

---

### Knowledge-freshness contract

<!-- TODO(P1-6): Define the knowledge-freshness contract referenced by 8 Citations rows (C1, C2, C3, C5, C7, C9, C10, C12) — (a) the file/format where verified-on dates live (frontmatter or inline `[verified YYYY-MM-DD]` markers), (b) the script that detects markers older than 90 days, (c) the gate/CI workflow that fails when one is overdue, (d) the disposition (re-fetch, re-quote, bump or revert); if the contract lives in a separate document, cite the path; the existing `knowledge-health` skill and `knowledge-health.py` script in ravenclaude-core are candidate substrate — disposition: in parallel with Phase 4 execution; this contract is referenced but not yet defined, leaving 8 load-bearing citations with no real settling gate -->

*(Placeholder — contract to be authored per P1-6 TODO above.)*

---

## Cross-cutting close-out gates

These run in Phase 7 (and again in CI on PR open). All must pass before merge.

| Gate | Command | Pass criterion |
|---|---|---|
| Prettier check (whole tree) | `npx --yes prettier --check . --log-level warn` | Exit 0 |
| Audit-gates meta-test | `scripts/audit-gates.sh` | Exit 0 (all gates including 48-51 prove fail-on-bad + pass-on-good) |
| Layout allow-list | AGENTS.md verification snippet | "Layout OK — every new file matches at least one allowed glob." |
| Manifest version-match (plugin.json ↔ marketplace.json) | CI's existing version-drift check | All 4 plugins' versions match between plugin.json and marketplace.json |
| JSON validity | `python3 -m json.tool` on every JSON file | All exit 0 |
| Shell syntax + executable | `bash -n plugins/*/hooks/*.sh && find plugins/*/hooks -name '*.sh' -exec test -x {} \;` | All exit 0 |
| Frontmatter schema | `scripts/check-frontmatter.py` | Exit 0 (new agent has required `audience` / `works_with` / `scenarios` / `quickstart`) |
| Knowledge-freshness markers | `count=$(grep -c '\[verified [0-9]' plugins/ravenclaude-core/agents/data-viz-designer.md) && [[ $count -ge 8 ]]` | At least 8 verified-date markers (one per §3 sub-section) |
<!-- TODO(P1-15): `grep -l` returns the filename if the pattern appears at least once and CANNOT count occurrences — a file with a single `[verified 2026-06-02]` would pass the original gate even if 7 of 8 sub-sections had no marker; replaced with `grep -c` + numeric comparison (fixed inline above); also define the 8 §3 sub-sections in the agent file so a reviewer can verify the minimum is achievable in the agent file's structure — disposition: in parallel with Phase 4 execution -->
| Citation `[unverified]` markers | `grep -c '\[unverified' plugins/ravenclaude-core/agents/data-viz-designer.md` | At least 2 (FT last-commit; IBCS hex codes) — matches strategic plan §3.4, §3.3 |
| Checkout freshness (advisory) | `scripts/check-checkout-fresh.sh` | Warns if behind origin/main; does not block |
| Gate 48 (linter bidirectional) | Sub-step of audit-gates | Bad fixture exits non-zero; good fixture exits zero |
| Gate 49 (WebFetch poisoned-body neutered) | Sub-step of audit-gates | Injection content does not appear in agent output |
| Gate 50 (tableau anti-drift; thin pointer ≤30 lines of overlap) | Sub-step of audit-gates | A regrown fixture fails; thin-pointer passes |
| Gate 51 (schema-enum drift) | Sub-step of audit-gates | Divergent fixture fails; aligned passes |
| Gate 52 (stack-enum drift) | Sub-step of audit-gates | Divergent inline-enum fixture fails; clean (anchor-referenced) passes |

### Citation-marker spot-check gates (G-CITE-*)

| Gate | Check | Pass |
|---|---|---|
| **G-CITE-1** | Agent file's IBCS-hex-code block contains `[unverified — third-party convention, IBCS PDF behind paywall]` | grep succeeds |
| **G-CITE-2** | Agent file's FT last-commit reference contains `[unverified — could not extract from GitHub HTML]` | grep succeeds |
| **G-CITE-3** | `power-bi-slop-anti-patterns.md` rows that cite community repos include commit SHA + verified-on date | grep matches `\[verified \d{4}-\d{2}-\d{2} at [0-9a-f]{7,40}\]` on every community-cited row |

---

## Effort estimates summary

<!-- TODO(P1-13): Add a single target-completion date ("within N working days of plan approval") and a midpoint checkpoint milestone ("Phase 3 complete before starting Phase 4"); without calendar anchors, "budget overrun" has no trigger and the cut-list authority (open question 6) cannot be exercised at the right time — disposition: in parallel with Phase 0 execution; Matt sets the calendar anchor when approving -->

| Phase | Order-of-magnitude | Honest hours | Cut-list candidate? |
|---|---|---|---|
| Phase 0 — Pre-build hygiene | quarter-day | ~1h | No (load-bearing for everything that follows) |
| Phase 1 — Linter + fixtures | half-day | ~3.5h | No (the linter is the agent's load-bearing artifact) |
| Phase 2 — Audit-gates Gates 48-51 | quarter-day | ~1.5h | Partial — Gate 49 fixture could defer per strategic plan §7 cut-list |
| Phase 3 — Skills + knowledge files | half-day | ~4.5h | Partial — IBCS skill could defer to v0.1.1 per strategic plan §7 cut-list |
| Phase 4 — Agent file | quarter-day | ~1.75h | No (the agent IS the deliverable) |
| Phase 5 — Tableau promotion + thin-pointer | half-day | ~3.5h | YES — defer to follow-up PR per strategic plan §7 cut-list |
| Phase 6 — Cross-links + version bumps | quarter-day | ~1.5h | No (links + versions are part of the marketplace contract) |
| Phase 7 — Close-out | quarter-day | ~1.25h | No (close-out is mandatory) |
| **TOTAL** | **~2 days focused** | **~17h** | **Cut-list saves up to ~5h → 12h minimum viable** |

### Cut-list sequence if budget overruns (in cut-first order)

1. **Cut Phase 5 (Tableau promotion + Gate 50)** — defer to follow-up PR. Saves ~3.5h + ~0.5h (Gate 50 from Phase 2). Strategic plan §2.4 still ships as design intent; promotion implementation deferred.
2. **Cut Phase 3.4 (IBCS skill) + the IBCS fixtures from Phase 1.5** — defer to v0.1.1. Saves ~1h + ~0.25h. Opt-in design means deferring doesn't break any v0.1.0 contract.
3. **Cut Gate 49 fixture (Phase 2.2)** — keep the WebFetch contract in §2.1 + the knowledge file, defer the fixture-backed gate to v0.1.0+1. Saves ~0.25h. NOT recommended (the gate is what makes the floor real).

**Minimum viable v0.1.0 (with cuts 1 + 2):** ~12h. Ships the agent + 3 skills + 3 knowledge files + linter + Gates 48 + 49 + 51 + cross-links + version bumps in 3 plugins. Tableau plugin stays unchanged; IBCS ships in v0.1.1.

---

## Open tactical questions for the build-plan panel (Panel 2)

These are the questions the build-plan panel should stress-test:

1. **Phase sequencing** — Phases 1 (linter) → 3 (skills) → 4 (agent) is the proposed order. Should the agent draft come first (so skills know what to support), or the skills (so the linter has documented callers)? Current ordering prioritizes the verifiable artifact (linter) first.
2. **Gate 50 anti-drift threshold** — 30 lines of overlap is the proposed limit. Is that too tight (forces aggressive thin-pointer rewrites)? Too loose (lets canon drift back into tableau over time)?
3. **Suppression mechanic adoption rate** — `_lintConfig` + `_lintIgnore` are non-standard JSON fields. Will existing PBIR tooling tolerate them, or do they need to live in a sidecar file? Risk: PBIR loaders reject unknown fields.
4. **Migration note placement** — tableau plugin's migration note: in `CHANGELOG.md` (if extant), `CLAUDE.md`, or release-notes-equivalent? Current proposal: `CHANGELOG.md` if extant, fall back to inline in plugin's `CLAUDE.md`.
5. **PR draft vs ready-for-review** — open as draft per CLAUDE.md remote-environment recipe; promote to ready after Panel 2 sign-off?
6. **Cut-list decision authority** — if budget overruns during execution, who decides which cut to take? Default: the executing agent flags Matt with the cut-list ordered and the trade-off summary, Matt picks. **Decision authority: Matt.** The executing agent surfaces the cut-list ordered with trade-off summary; Matt picks.

---

## Panel 2 cold review — P0/P1 gaps & recommendations

Panel 2 is a fresh-independent expert panel composed of four lenses — **testability (tester_qa)**, **project execution (project_manager)**, **evidence and grounding (deep_researcher)**, and **surface design (prompt_engineer)**. Each lens read the build plan **cold**, with no access to Panel 1's strategic-plan critique or to the build-plan authors' framing notes. That isolation is deliberate: it surfaces gaps the authors did not anticipate and prevents Panel 2 from inheriting Panel 1's blind spots. Findings are deduplicated across lenses below, but every lens that independently raised the same gap is preserved in parentheses — multiple-lens hits strengthen the signal. P0/P1 ordering puts trust-boundary and executability-blocking issues first, then alphabetical within tier.

### P0 gaps (executability blockers — must close before Phase 1 starts)

#### P0-1 · G-PRE-5 hardcodes a path that does not exist in the repo *(tester_qa)*

**Evidence (historical — closed in this revision).** G-PRE-5's gate command originally read `python3 -c "import re; t=open('<wrong-path>').read(); ..."` pointing at the ravenclaude-core path; the same wrong path was cited by C22 and C23, by `lint.py`'s runtime path in task 1.1, and by Gate 51. The file actually lives at `plugins/power-platform/knowledge/pbir-enhanced-reference.md`. Running the original gate command in this session produced `FileNotFoundError` for the ravenclaude-core path. `lint.py` (task 1.1) would have parsed the wrong file at runtime and exited 3 on every invocation. **Resolution applied:** every reference (G-PRE-5 gate command, C22, C23, Gate 51 description, `lint.py` runtime path in Phase 1.1) now points to `plugins/power-platform/knowledge/pbir-enhanced-reference.md`. The cross-plugin read is documented explicitly in `lint.py`'s purity-contract docstring (see Phase 1.1).

**Recommendation (option (b) adopted).** Two options were considered: (a) add a Phase 0 task to copy `pbir-enhanced-reference.md` into the ravenclaude-core knowledge directory (update `.repo-layout.json` and declare the cross-plugin dependency), or (b) update G-PRE-5, C22, C23, Gate 51, and `lint.py`'s runtime path to `plugins/power-platform/knowledge/pbir-enhanced-reference.md` and document the cross-plugin read in `lint.py`'s purity-contract docstring. Option (b) is the minimal change; option (a) avoids a cross-plugin filesystem dependency. **Option (b) was adopted** — all references now point at the power-platform path; `lint.py`'s purity-contract docstring documents the cross-plugin read.

#### P0-2 · No named human owner on any phase, task, or decision *(project_manager)*

**Evidence.** Every task row's owner is implicitly "the executing agent." The cut-list decision entry reads: "Default: the executing agent flags Matt with the cut-list ordered and the trade-off summary, Matt picks." No phase, task, or gate names a single accountable human. Open tactical question 6 explicitly defers the cut-list decision authority to runtime.

**Recommendation.** Add a single named owner (Matt or a named executor) to the phase-level header row and to open tactical question 6. For an AI-executed Ultraplan build, the owner is still the human who merges the PR — declare that explicitly. Without a named owner, there is no one to RAID-log a slip against.

#### P0-3 · 12 linter fixtures have no names, no content specs, and no check-to-fixture mapping *(tester_qa)*

**Evidence.** Task 1.5: "Write 12 fixtures under tests/fixtures/data-viz/ | 12 JSON files | n/a | Each bad fixture fails exactly the targeted check; good fixture passes all 7 | run lint.py against each | 0.75h." Only 3 of the 12 are named anywhere in the plan: `hand-tuned-vertical-grid-passes.json`, `poisoned-fetched-body.json`, `enum-drift-divergence.json`. The 7 check IDs (`check-1` through `check-7`) appear in the Finding dataclass but no section defines what each check tests by name. Gate 48's pass criterion ("Bad fixture exits non-zero; good fixture exits zero") cannot verify that the correct check fired — a fixture that triggers `check-2` when `check-3` is the target passes the gate while masking a dead code path.

**Recommendation.** Add a **fixture manifest table** before task 1.5 with columns: `filename | targets-check | input-shape | expected-Findings | exits`. One row per fixture. Also add a **linter check-definitions table** before task 1.1 with columns: `check-id | name | function | applies-to | default-severity`. These two tables make Gate 48 verifiable and let reviewers confirm bidirectionality per check.

#### P0-4 · Agent OUTPUT envelope has no wire format, no field types, and no required/optional discipline *(prompt_engineer)*

**Evidence.** § Schemas / contracts → "data-viz-designer agent invocation contract" lists OUTPUT fields as prose key names: `ft_category`, `chart_family`, `cleveland_mcgill_rank   1-10 with citation`, `layout_arithmetic   {page_w, page_h, margin, gap, n_cols, n_rows, computed positions}`, `palette             {family, ColorBrewer ref, hex codes, colorblind_safe: bool}`, etc. The plan does not state (a) whether this is JSON, YAML, Markdown-with-sections, or a fenced code block in transcript prose; (b) which fields are required vs optional; (c) the type of `cleveland_mcgill_rank   1-10 with citation` — is it `{rank: int, citation: str}` or a single string `"3 (Heer 2010)"`?; (d) the shape of `layout_arithmetic.computed positions` (a list? a dict keyed by `visual_id`?). The consumers on the other side are `power-bi-engineer` (Phase 6.1) and `dashboard-builder` (Phase 6.3); both will need to parse this. With no wire format, the two consumers will diverge.

**Recommendation.** Add a concrete JSON Schema (or TypedDict) for the agent's structured output, including: (1) `serialization`: JSON in a fenced ```json block at the end of the agent transcript; (2) required vs optional per field — at minimum `ft_category`, `chart_family`, `layout_arithmetic`, `wcag_pass`, `linter_report`, `ibcs_mode` required; `cleveland_mcgill_rank`, `palette`, `webfetch_notes` optional; (3) replace prose `cleveland_mcgill_rank   1-10 with citation` with explicit shape `{rank: int (1..10), citation_doi: str}`; (4) define `layout_arithmetic.positions` as `list[{visual_id: str, x: int, y: int, width: int, height: int}]`; (5) `linter_report` MUST be `list[Finding]` in the JSON shape of the dataclass (snake_case keys); (6) state whether unknown fields are tolerated (forward-compat) or rejected (strict). Without (5) in particular, the `linter_report` round-trip across the agent boundary is undefined.

#### P0-5 · `--stack` enum is the same contract in three places and is not authoritatively defined anywhere *(prompt_engineer)*

**Evidence.** The agent invocation contract lists `stack              one of: pbir | tremor | recharts | evidence | superset | metabase`. Phase 6.1 says power-bi-engineer composes the agent `with --stack=pbir contract`. Phase 6.3 says dashboard-builder composes with `--stack=tremor|recharts|...` (with literal ellipsis). Phase 3.1's chart-from-intent skill `Composes` column references `agent --stack=* contract`. The plan does not designate a single source of truth, does not specify whether `--stack=` is a CLI flag for a Python program or a Markdown-convention argument to a sub-agent, and does not say what happens when an unrecognized stack is passed. With four files claiming the enum and Phase 6.3 using a literal `...`, the four locations will drift.

**Recommendation.** Designate `plugins/ravenclaude-core/agents/data-viz-designer.md` § Invocation contract as the SINGLE source of truth for the `stack` enum, and reference it by anchor from the three other locations rather than restating values. Replace Phase 6.3's literal `--stack=tremor|recharts|...` with the exact same enum list. Add the error contract: "Unknown `stack` value → agent emits `stack_warning: \"unknown stack 'X'; returning stack-agnostic design\"` in its output envelope and proceeds as if `stack` were absent." Add a `stack` schema-drift gate (Gate 52) that diffs the enum lists across the four files. Clarify upfront whether `--stack=pbir` is a CLI flag passed to a Python entry-point or a natural-language argument the Team Lead injects — the build plan currently treats it as both.

#### P0-6 · Linter `--format=json` is named but the JSON shape is undefined *(prompt_engineer)*

**Evidence.** § Linter CLI says `--format=text|json        Output format. Default: text.` The `Finding` dataclass is `frozen=True` but the document never says how `Finding` serializes when `--format=json` is selected: is it `{"findings": [...], "exit_code": 1}` or a bare array? Are dataclass field names emitted as-is (`check_id`) or transformed to camelCase? Is `visual_id: str | None` emitted as `null` or omitted when None? Is there a top-level summary (counts by severity, schema version)? The `linter_report` field in the agent's structured output is `Finding[]` — the agent parses JSON from `lint.py --format=json` and re-emits it. Without a defined JSON shape, the lint → agent → consumer round-trip is undefined.

**Recommendation.** Add a JSON output envelope contract to § Linter CLI:

```json
{
  "schema_version": "1.0.0",
  "linter_version": "<pinned constant>",
  "input_path": "<resolved absolute path>",
  "exit_code": 0,
  "summary": {"info": 0, "warning": 0, "error": 0},
  "findings": [{"check_id": "check-1", "severity": "error", "page": "Overview", "visual_id": "kpi-1", "message": "...", "fix_hint": "..."}]
}
```

Specify: snake_case keys (matching dataclass), `null` instead of omission, `schema_version` is the contract version not the linter version, `exit_code` mirrors the process exit code so log readers don't need both. Then Gate 48 can assert the JSON shape, not just the exit code.

### P1 gaps (close before merge — verifiability or consumer-impact risks)

#### P1-1 · No explicit dependency graph — parallel-safe vs sequential tasks are not distinguished *(project_manager)*

**Evidence.** The plan states "Phases are sequenced so each builds on the prior" but does not specify which tasks within a phase are independent. Phase 3 (skills + knowledge files) lists 7 tasks with no indication which can parallelize. Phase 6 (cross-links + version bumps) has 8 tasks all independent of each other but all blocked on Phase 4. A coder (or Ultraplan) cannot distinguish serial from parallel work.

**Recommendation.** Add a "depends on" column to each phase task table, or a short prose note per phase. At minimum, call out the critical path: Phase 0 → Phase 1 (linter) → Phase 3.2 (SKILL.md pointing at linter) → Phase 4.1 (agent) → Phase 6.1/6.3 (cross-links). Everything else is parallelizable once its inputs exist.

#### P1-2 · Citations table omits URLs for sources the executor must re-fetch *(deep_researcher)*

**Evidence.** The Citations table's "Primary source" column has values like `w3.org/TR/WCAG22/`, `colorbrewer2.org`, `ibcs.com/standards`, `doi.org` — domain stubs, not retrievable URLs. C8 references `github.com/Financial-Times/chart-doctor` with no path; C18 says `github.com/data-goblin/power-bi-agentic-development` with no SHA in the table; C15-C17 say only `doi.org` rather than the resolvable `https://doi.org/10.1145/...` form. A coder cannot re-verify a claim without re-running discovery.

**Recommendation.** Replace each "Primary source" cell with the exact fully-qualified URL (e.g. `https://www.w3.org/TR/WCAG22/#contrast-minimum`, `https://doi.org/10.1145/1753326.1753357`, `https://github.com/Financial-Times/chart-doctor/tree/<sha>/visual-vocabulary`). For repo-internal citations (C22, C23, C24), use the `file:line` form per AGENTS.md accuracy discipline. Add a "Quoted excerpt" column with the exact string to grep for after re-fetching — this is what makes G-CITE-1/2 verifiable rather than honor-system.

#### P1-3 · Conditional G-PRE-1 disposition creates an untracked scope branch never reconciled *(project_manager)*

**Evidence.** G-PRE-1 disposition reads: "If skill itself doesn't exist, defer the auto-trigger path and ship IBCS as explicit-user-request-only in v0.1.0." This silently alters Phase 3.4 (ibcs-variance-reports SKILL.md), the IBCS activation breadcrumb contract, and the Sága log schema — all of which assume the auto-trigger path exists. No task conditionally removes the auto-trigger if the gate fails, and no checkpoint verifies the branch was taken consistently.

**Recommendation.** Add a Phase 0 task whose acceptance test is: "Document which G-PRE-1 disposition path was taken and confirm all downstream tasks reflect that choice." If the skill is absent, add an explicit line to Phase 3.4's acceptance test: "IBCS auto-trigger removed; SKILL.md documents explicit-only mode." Name that conditional as a RAID Issue if the gate fails.

#### P1-4 · `finance_context` template update is contingent on G-PRE-1 failing — but G-PRE-1 always passes *(tester_qa)*

**Evidence.** G-PRE-1's fail disposition is "Add environment-context.md schema definition to ravenclaude-core in this PR (defines `finance_context: ibcs|none` key, default `none`)." G-PRE-1 currently passes (the skill exists — confirmed by running the gate). Since the fail disposition only fires when G-PRE-1 fails, the template update never triggers. No Phase 3 or Phase 5 task unconditionally updates `plugins/ravenclaude-core/templates/environment-context.md`. The IBCS `finance_context_tag` trigger silently never activates for consumers whose template predates this PR.

**Recommendation.** Promote the template update to an unconditional task in Phase 3 (after task 3.4). The task: add `finance_context: ibcs | none  # default: none` to the template with an explanatory comment. Acceptance test: `grep 'finance_context' plugins/ravenclaude-core/templates/environment-context.md`.

#### P1-5 · Gate 49 acceptance test is underspecified and may require live LLM inference *(tester_qa + project_manager)*

**Evidence.** Task 2.2 / Gate 49 pass criterion: "Fixture's `<system-reminder>` content does NOT appear in agent output." Existing injection gates in audit-gates.sh test pre-LLM string screening via deterministic CLI exit codes — none assert on agent output. Gate 49 as written requires invoking the agent (LLM call) and checking its response, which is non-deterministic, availability-dependent, and token-budget-sensitive. The plan also never specifies what "agent output" means in a static CI fixture context (mock response file? regex over stdout? live agent invocation?) or what the "good fixture" looks like (clean body with no injection).

**Recommendation.** Redesign Gate 49 to test a **deterministic sanitizer layer**. Define `sanitize_webfetch_body(raw: str) -> str` in `lint.py` or a shared util; place its tests in `tests/fixtures/test_pbir_lint.py`; have Gate 49 invoke that function against `poisoned-fetched-body.json` and assert injection strings are absent from the sanitized output. Pair it with a clean fixture (`clean-fetched-body.json`) for bidirectionality. Document in `webfetch-return-envelope-hardening.md` that the sanitizer gate is the security floor, not post-LLM observation.

#### P1-6 · `knowledge-freshness contract re-verifies every 90 days` is referenced as a gate but never defined *(deep_researcher)*

**Evidence.** Eight Citations rows (C1, C2, C3, C5, C7, C9, C10, C12) list this as their settling gate — the dominant settling mechanism in the table. The build plan never defines what file holds the contract, who runs the re-verification, what triggers it, what the failure mode is if a check is overdue, or how a `[verified 2026-06-02]` marker gets bumped. The Phase 7 close-out gates don't include a freshness check; the Cross-cutting gates list `grep -l '\[verified [0-9]'` (presence, not freshness).

**Recommendation.** Add a "Knowledge-freshness contract" section that specifies (a) the file/format where verified-on dates live (frontmatter or in-line `[verified YYYY-MM-DD]` markers), (b) the script that detects markers older than 90 days, (c) the gate/CI workflow that fails when one is overdue, (d) the disposition (re-fetch, re-quote, bump or revert). If the contract lives in a separate document, cite the path. Without it, eight load-bearing rows have no real settling gate — only a name.

#### P1-7 · C11 (`displayOption` enum) pairs two sources without saying which to trust if they conflict *(deep_researcher)*

**Evidence.** Citation C11 reads "Power BI JS SDK + PBIR Enhanced schema" with Gate 51 (schema-enum drift) as settling gate. The two named sources are independent surfaces that historically drift. Neither is given a URL or version pin. Gate 51 watches drift between `pbir-enhanced-reference.md` § 1 and `lint.py` — it does NOT watch drift against the JS SDK. If the JS SDK changes casing in a future release, the linter and the agent's published contract diverge from the SDK with no detection.

**Recommendation.** Split C11 into C11a (JS SDK enum, with `powerbi-client` GitHub URL + commit SHA + filename:line) and C11b (PBIR Enhanced schema, with `pbir-enhanced-reference.md` file:line). Declare which is authoritative for the agent's output contract and which is informational. If they ever diverge, name the disposition.

#### P1-8 · C14 contoso-examples denominator is asserted without naming exclusions or quoting measurements *(deep_researcher)*

**Evidence.** Citation C14: "contoso-examples Overview horizontal grid: 24px margin + 16px gutter + 312px stride | github.com/bernatagulloesbrina/contoso-examples (7 of 9 visual.json) | verified 2026-06-02." The 24/16/312 values become hard-coded into a fixture and the linter's default tolerances (Phase 1.5). The citation does not name which 2 of 9 were excluded and why, quote the JSON field being measured, or pin a commit SHA. If the upstream repo changes, the "verified" marker becomes a fiction and fixtures embed unrecoverable measurements.

**Recommendation.** Expand C14 to specify the commit SHA, the exact JSON path measured (e.g. `report/pages/<page>/visuals/<id>/visual.json#position.x`), the 7 included file paths, and the 2 excluded paths with exclusion rationale. Add a fixture-derivation note in Phase 1.5 that names the SHA.

#### P1-9 · C25 ("Gate 48 reserved") is `[unverified — assumed]` yet drives the entire audit-gates phase *(deep_researcher)*

**Evidence.** C25: "audit-gates.sh Gate 48 reserved (47 = latest in main) | scripts/audit-gates.sh | unverified — assumed | G-PRE-2 confirms next free gate number." Phase 2 (4 tasks, 1.5h) is keyed to Gates 48, 49, 50, 51. G-PRE-2's fail disposition is a non-trivial cross-document rewrite, and the Citations table is the only place that captures the assumption.

**Recommendation.** Run G-PRE-2 as Step 0 of Phase 0 (before any other gate) and paste its output into the PR description. If 48-51 are not free, the build plan must specify the find-and-replace target list explicitly — strategic plan §4, every Phase-2 task row, every Cross-cutting close-out row, every gap-debug table row mentioning Gate 49 or 51, the Citations table "Gate that settles it" column for C4/C7/C11. Without a named replacement list, this is a silent-failure mode.

#### P1-10 · `_lintConfig` / `_lintIgnore` sidecar fallback is missing despite the open question naming the risk *(prompt_engineer)*

**Evidence.** Open tactical question 3 names the risk: "PBIR loaders reject unknown fields." The plan ships these non-standard fields in v0.1.0 (Phase 1.4) without resolving the risk or specifying a sidecar fallback. If a Power BI loader rejects an `_lintConfig` key on `page.json`, the consumer's PBIR build breaks AND the linter's suppression mechanism doesn't work — both contracts fail at once.

**Recommendation.** Add G-PRE-7: "Verify that pbi-tools / pbicli / Power BI Desktop tolerate unknown root-level keys with a `_` prefix in page.json." If verified, ship in-line. If not, switch to a sidecar contract: `<page>.lintconfig.json` colocated with `page.json`, same schema, linter loads it if present. Document the sidecar path in § Schemas / contracts as the fallback. The linter implementation in Phase 1.4 should support BOTH sources (sidecar preferred, in-line tolerated) so the contract is forward-compatible.

#### P1-11 · `page.json` shape consumed by linter is implied but never defined *(prompt_engineer)*

**Evidence.** The `_lintConfig` block example shows a top-level `page.json` with `visuals[]` inline. The linter's input contract (`input-path  Path to a single visual.json, a page directory containing visual.json files, or a fixture directory`) speaks of `visual.json` files (plural), implying one file per visual. These two are mutually exclusive. The actual PBIR Enhanced layout uses one `visual.json` per visual under a directory tree.

**Recommendation.** Reconcile § Linter CLI's input contract with the `_lintConfig` schema example. Either (a) the linter walks a page directory (`<page>/page.json` + `<page>/visuals/<id>/visual.json` files) and `_lintConfig` lives on `page.json` while `_lintIgnore` lives on each `visual.json`; or (b) the linter accepts a synthetic flattened `page-with-visuals.json` for fixture convenience and a real PBIR tree for production. State which and add directory-walking logic to Phase 1.1's acceptance test.

#### P1-12 · `environment-context.md` `finance_context` key has YAML semantics in a `.md` file with unspecified frontmatter discipline *(prompt_engineer)*

**Evidence.** § Schemas / contracts specifies `finance_context: ibcs | none` as YAML in a `.md` file. The plan does not say (a) is this YAML frontmatter delimited by `---`, freeform YAML in a fenced code block, or `key: value` line-scanned?; (b) what other keys live there; (c) runtime behavior if the file is absent (G-PRE-1 default `none` is design intent, not the runtime contract); (d) what happens on unrecognized values. The skill's auto-activation depends on parsing this reliably.

**Recommendation.** Specify the parse contract: "environment-context.md is Markdown with a YAML frontmatter block at the top (delimited by `---`). The `ibcs-variance-reports` skill reads the frontmatter, defaults `finance_context` to `none` if absent, treats unknown values as `none` and emits a one-line warning to the agent transcript. The skill does not parse the Markdown body." Add fixtures: `environment-context-missing.md`, `environment-context-ibcs.md`, `environment-context-unknown.md`.

#### P1-13 · Total effort estimate has no slack model and no milestone dates — only hours *(project_manager)*

**Evidence.** "Grand total: ~17h (within the 20h-with-contingency budget from strategic plan §7)." No milestone dates, no working-day anchors, no slack model. The 20h budget is referenced from the strategic plan (which Panel 2 was not permitted to read). The build plan never states when Phase 0 starts, when Phase 4 must be done, or what "overrun" means in calendar terms.

**Recommendation.** Add a single target-completion date ("within N working days of plan approval") and a midpoint checkpoint milestone ("Phase 3 complete before starting Phase 4"). Without calendar anchors, "budget overrun" has no trigger and open question 6's cut-list authority cannot be exercised at the right time.

#### P1-14 · Task 3.4 acceptance criterion references trigger-path fixtures that no task creates *(tester_qa)*

**Evidence.** Task 3.4's acceptance test: "Same; trigger-path fixture tests pass." Gate column: `n/a`. No task in any phase creates IBCS trigger-path fixtures. The breadcrumb regex is precisely defined but nothing creates inputs for the 3 trigger paths or asserts the regex matches. Structurally orphaned.

**Recommendation.** Add task 3.4a: create 3 small fixtures under `tests/fixtures/data-viz/ibcs/` — one per trigger path (`user_request`, `explicit_mention`, `finance_context_tag`). Each fixture defines input conditions and asserts the breadcrumb regex matches. Wire into pytest invocation in Phase 7 close-out. Move the Gate column from `n/a` to the new test invocation.

#### P1-15 · Knowledge-freshness close-out gate uses `grep -l` and cannot count to 8 *(tester_qa)*

**Evidence.** Close-out gate: `grep -l '\[verified [0-9]' plugins/ravenclaude-core/agents/data-viz-designer.md` with pass criterion "At least 8 verified-date markers (one per §3 sub-section)." `grep -l` returns the filename if the pattern appears at least once — it cannot count occurrences. A file with a single `[verified 2026-06-02]` passes this gate even if 7 of 8 sub-sections have no marker.

**Recommendation.** Replace with: `count=$(grep -c '\[verified [0-9]' plugins/ravenclaude-core/agents/data-viz-designer.md) && [[ $count -ge 8 ]]`. Also define the 8 §3 sub-sections so a reviewer can verify the minimum is achievable in the agent file's structure.

#### P1-16 · `Finding.fix_hint` is contractually required but has no shape/length/style guarantee *(prompt_engineer)*

**Evidence.** Dataclass declares `fix_hint: str       # One-line actionable suggestion`. With no contract on length, style (`"Move visual to x=24"` vs a 30-word paragraph), or whether it may contain newlines / markdown / code fences, two implementers will diverge and the downstream UI renders inconsistently.

**Recommendation.** Tighten: `fix_hint: str  # single line, ≤200 chars, plain text (no markdown, no newlines, no code fences), imperative voice ("Move kpi-1 to x=24"). For multi-line guidance, link to the knowledge file from the message field.` Add a unit test in Phase 1.2 asserting `'\n' not in finding.fix_hint and len(finding.fix_hint) <= 200` across the fixture corpus.

#### P1-17 · Agent invocation contract conflates CLI-style ARGUMENTS with natural-language agent inputs *(prompt_engineer)*

**Evidence.** § Invocation contract uses CLI-style formatting (`ARGUMENTS`, `intent ... one of: ...`, `stack ... OR absent`, `ibcs ... optional`) but the agent is spawned by the Team Lead with a natural-language prompt — there is no argv. Either (a) these are conventions the caller must include in a structured preamble, or (b) the agent parses free text to extract them — the plan implies both.

**Recommendation.** Replace the CLI-style block with an explicit **invocation preamble template** the caller injects literally:

```
---
intent: deviation
data_shape: 12-month monthly actuals vs PY, single business unit
stack: pbir
ibcs: auto
---
<free-form goal narrative>
```

Add a parse contract: "data-viz-designer reads the YAML preamble (if present) and treats fields as authoritative over conflicting natural-language description; if absent, falls back to extracting from prose and marks extracted values with `[inferred]` in the output envelope." Update Phase 6.1 and Phase 6.3 to add the preamble template to each consumer's instructions.

### P2 gaps (worth a one-line follow-up; do not block the PR)

- SC 1.4.6 in output contract has no citation, no skill coverage, no fixture *(tester_qa)*
- Inline pytest in `lint.py` conflicts with established repo test pattern and has no invocation path *(tester_qa)*
- 7 linter check names are undefined anywhere in the plan *(tester_qa)*
- data-platform version bump listed as "(current) → +0.0.1" without stating baseline *(project_manager)*
- Tableau-only consumer migration note (task 5.7) cut along with Phase 5, leaving broken pointers *(project_manager)*
- Open tactical questions 1-5 unresolved and not RAID-logged *(project_manager)*
- C4 IBCS SUCCESS expansion doesn't quote the corrected wording *(deep_researcher)*
- C9 + C10 Microsoft Learn page-date pins lack archive.org snapshots *(deep_researcher)*
- C22-C24 repo-state citations don't pin commit SHAs *(deep_researcher)*
- C6 IBCS hex codes pin no SHA on the third-party source *(deep_researcher)*
- C12 Q&A retirement date is a single-vendor source for a high-leverage claim *(deep_researcher)*
- `wcag_pass` schema is closed against future WCAG SCs and lacks C-WCAG-3 backing for SC 1.4.6 *(prompt_engineer)*
- Sága log filename uses `T` + `-HH-MM-SS` (Windows-friendly) while body uses ISO 8601 — undocumented deviation *(prompt_engineer)*

### Where Panel 2 disagreed with itself

**On inline pytest vs separate test files.** `tester_qa` recommends moving unit tests out of `lint.py` into `tests/fixtures/test_pbir_lint.py` to match the repo's established pattern (the test_security_deny_floor.py shape). `prompt_engineer` is silent on this but implicitly assumes inline tests (its `fix_hint` length test recommendation says "add a unit test in Phase 1.2" without specifying location). **Panel 2's resolution:** follow `tester_qa` — the repo pattern is the stronger evidence (test_security_deny_floor.py is in main and runnable via pytest), and inline tests in `lint.py` violate the linter's own purity-contract docstring discipline if the test code imports test-only deps.

**On Gate 49's implementation.** `tester_qa` (P1-3 in its enumeration) wants Gate 49 to test a deterministic `sanitize_webfetch_body` function. `project_manager` (its own P1-4) wants Gate 49 to remain content-comparison-based but with a precisely named fixture pair and a clearly defined "agent output" (mock response file vs regex vs live invocation). **Panel 2's resolution:** the testability lens wins — a deterministic sanitizer gate is verifiable in CI today, while content comparison against "agent output" remains nondeterministic regardless of how it's specified. The merged P1-5 above adopts the sanitizer approach AND incorporates the project_manager-requested named-fixture-pair discipline.

**No other lens-vs-lens contradictions surfaced.** Overlapping findings (e.g., the citations-without-URLs gap touches both `deep_researcher` and `prompt_engineer` in spirit) were consolidated into a single recommendation rather than being treated as disagreement.

### Net recommendation from Panel 2

The build plan is **not executable as-is**, but the structural bones are sound — the gate network, fixture philosophy, typed Finding dataclass, and rollback story are above the median for tactical artifacts at this scope. The six P0s are all closable in a single editing pass without rebuilding the plan: a path correction (P0-1), a named owner addition (P0-2), a fixture manifest + check-definitions table (P0-3), an output-envelope JSON Schema (P0-4), a `--stack` source-of-truth designation with a new Gate 52 (P0-5), and a linter JSON output contract (P0-6). Estimated rework: 1.5-2h of editing, no Phase 1+ code change required. The 17 P1s are real but do not block Phase 1 from starting — most can be closed in parallel with execution as long as P0 closure precedes Phase 0 gate runs. **Recommendation:** close the six P0s in a single revision pass, queue the P1s into the build plan itself as inline TODO comments tied to their owning phase, then start Phase 0. **Confidence: 0.78** — high enough to act on, with the residual 0.22 reflecting (a) the knowledge-freshness contract gap (P1-6) which may surface as a larger architectural question once defined, and (b) the `_lintConfig` sidecar question (P1-10) which could force a Phase 1.4 redesign if G-PRE-7 fails.
