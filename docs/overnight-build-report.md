# Overnight build report — 2026-05-20 → 2026-05-21

**Run owner:** autonomous overnight pass (Claude Code, Opus 4.7)
**Started:** 2026-05-20 evening (Matt asleep)
**Finished:** 2026-05-21 morning
**Branch base:** `origin/main` (post-PR-15, sha `339ab49`)
**Repo state at finish:** clean on all three plugin branches; 3 PRs open.

> This is the document Matt reads in the morning. The companion is [`./plugin-roadmap-analysis.md`](./plugin-roadmap-analysis.md), which is the prioritization that drove the build.

---

## 1. Mission

Analyze which Claude Code plugins Raven Power LLC should build next, build the top three, iterate them against the marketplace's own quality methodology until they feel polished, push each as its own PR for Matt's review.

## 2. Outcome at a glance

- **Analysis doc shipped:** [`docs/plugin-roadmap-analysis.md`](./plugin-roadmap-analysis.md)
- **3 plugins built**, each a complete domain team with CLAUDE.md, README.md, plugin.json, agents/, skills/, templates/, hooks/, and `hooks.json` declaration. 20 specialist agents across the three.
- **3 PRs opened against `main`**, each branch isolated from the other two:
  - PR #14 — `feat(finance)` — <https://github.com/mcorbett51090/RavenClaude/pull/14>
  - PR #15 — `feat(regulatory-compliance)` — <https://github.com/mcorbett51090/RavenClaude/pull/15>
  - PR #16 — `feat(web-design)` — <https://github.com/mcorbett51090/RavenClaude/pull/16>
- **No merges.** All three left open for review per instructions.

## 3. Phase 1 — Analysis

The repo's `README.md` listed `finance`, `edtech`, `salesforce` as the planned next plugins. I evaluated those plus four others suggested by Raven Power's actual service mix:

| Rank | Plugin | Verdict |
|---|---|---|
| 1 | **`finance`** | Build (on roadmap, Matt's FP&A / controller background) |
| 2 | **`regulatory-compliance`** | **Build** — Matt's 2 yrs inside the BMA is rare expertise; very high differentiation; not previously on the roadmap |
| 3 | **`web-design`** | Build (active service line) |
| 4 | `edtech` | Defer (no current engagement; no Matt-specific edge) |
| 5 | `salesforce` | Defer (competes with the Power Platform plugin) |
| 6 | `data-engineering` | Defer (overlaps with core `backend-coder` + power-platform power-bi-engineer) |
| 7 | `microsoft-fabric` | Defer (better as a power-platform expansion) |
| 8 | `agentic-ai` | Defer (overlaps with `ravenclaude-core/prompt-engineer`) |

The full ranking criteria + scope per top-3 plugin is in the analysis doc. The headline choice that diverges from the README's roadmap: **drop `edtech` + `salesforce`, add `regulatory-compliance` + `web-design`** for this build pass. Rationale: Matt's regulator-side experience (BMA) is the most defensible asset Raven Power has, and `web-design` is something the practice actively sells today. `edtech` and `salesforce` get rebuilt against the same criteria the next time the priority comes up.

## 4. Phase 2 — Build

Each plugin follows the marketplace conventions: YAML-frontmatter agent definitions ending in the cross-plugin Structured Output Protocol JSON block, plugin-internal CLAUDE.md with §1 roster / §2 routing / §3 house opinions / §4 anti-patterns / §5 Grounding Protocol / §6 Output Contract / §7 hooks / §8 skills / §9 templates / §10 escalation / §11 references, a `hooks.json` that consumers' Claude Code merges automatically, a SemVer'd `plugin.json` requiring `ravenclaude-core@>=0.5.0`, and registration in `.claude-plugin/marketplace.json` + `docs/architecture.md` Status table.

### 4.1 `finance` — corporate finance & FP&A (v0.1.0)

7 specialist agents (FP&A analyst, financial modeler, controller, treasury analyst, valuation analyst, audit-prep specialist, board-pack composer), 4 skills (month-end close, variance commentary, model review, board-pack composition), 8 templates, 1 advisory hook (`flag-finance-anti-patterns.sh`: hardcoded rate-like numbers in models, plaintext SSN/IBAN/PAN, variance commentary without `Sources:`, forecast/budget without `Assumptions:`).

Plugin-specific SOP fields: `sources_cited`, `materiality_threshold`, `confidentiality`. House opinions: source-cite every number; no hardcoded mechanics; reconciliation before commentary; materiality declared up front; audit trail in every workpaper; numbers don't ship without commentary; one source of truth per metric; plain English first.

### 4.2 `regulatory-compliance` — financial-regulatory & compliance (v0.1.0)

6 specialist agents (AML/KYC, regulatory reporting, risk-and-controls, policy & procedure writer, examination prep, Bermuda-insurance), 4 skills (AML program review, regulatory mapping, SAR narrative drafting, examination readiness), 8 templates, 1 defensive **PreToolUse** hook (`scrub-confidential-pre-write.sh`) that scans pending writes for SSN/EIN/IBAN/PAN/Bermuda TIN/passport/DL/wire patterns *before* they land on disk.

Plugin-specific SOP fields: `regulatory_citations`, `jurisdiction`, `confidentiality`, `legal_advice_gate` (every agent declares whether it's staying inside the compliance lane or needs counsel). House opinions: cite the regulation (regulator's primary source, never a third-party summary); privilege is a design constraint; three lines of defense are not a slogan; risk appetite drives controls; remediation has a date and an owner; default to written; sanctions screening is binary; privacy by default; **don't give legal advice**; jurisdiction matters; risk is quantified (inherent + residual + target).

This is the differentiated plugin — Matt's BMA field experience is the asset. The Bermuda-insurance specialist alone covers Class 1-4 captives, Class A-E long-term insurers, ILS / SPI, SAC, BSCR, EBS, ICS, CISSA, and Solvency II equivalence with regulator-grade citation discipline.

### 4.3 `web-design` — web design & build (v0.1.0)

7 specialist agents (web architect, UX designer, visual designer, frontend implementer, content strategist, accessibility auditor, performance engineer; technical SEO split across web-architect + content-strategist), 4 skills (design-system audit, accessibility review, Core Web Vitals tuning, technical SEO audit), 8 templates, 1 advisory hook (`check-web-anti-patterns.sh`: oversized rasters, `<img>` missing `alt`, hardcoded hex outside `tokens.*`, missing `<title>`/`<meta description>`, accidental `noindex`).

Plugin-specific SOP fields: `standards_cited`, `budget_impact`, `tested_on`. House opinions: accessibility is P1 (WCAG 2.2 AA floor); performance has a budget; mobile-first; design tokens not hardcoded values; semantic HTML before ARIA; content informs design; no layout shift after first paint; one CTA per screen; static-first (SSG > SSR > CSR); SEO + a11y converge; third-party scripts are debt; one source of truth per design decision; print + reduced-motion not afterthoughts.

## 5. Phase 3 — Iterate & polish (self-improvement loop)

The marketplace's quality methodology (assembled from `validate-marketplace.yml`, `docs/best-practices/ci-gate-audit.md`, `docs/best-practices/plugin-versioning.md`, `docs/best-practices/hook-authoring.md`, the staging-contributions flow, and the CLAUDE.md house-opinions pattern) gave me five concrete passes:

| Pass | Method | What it caught |
|---|---|---|
| 1 | JSON validation (mental — local `python3` / `jq` unavailable on this box, but visual inspection + the CI workflow runs it on push) | None — all manifests well-formed |
| 2 | `bash -n` syntax + `chmod +x` check on every new hook | None after initial commit — already clean |
| 3 | Email-leak guard (`grep -r matt@ravenpower.net` over manifests) | None — no leaks |
| 4 | Cross-reference sweep (every internal markdown link checked against actual files) | **8 broken links across 3 plugins** — fixed in dedicated polish commits per plugin |
| 5 | Hook gate-audit pattern (synthesize a bad fixture + a good fixture, run the hook, verify it flags + passes correctly) | All 3 hooks behaved correctly on both fixtures after polish; one minor tuning iteration on the finance regex |

Iteration counts (commits per plugin):

- **`finance`** — 2 commits (initial build + cross-reference polish). 1 polish iteration.
- **`regulatory-compliance`** — 2 commits (initial build + cross-reference + template-placeholder cleanup). 1 polish iteration.
- **`web-design`** — 2 commits (initial build + cross-reference + design-system-spec placeholder removal). 1 polish iteration.

Beyond that, pass-2 SOP consistency check confirmed all 20 agents (across all 3 plugins) emit the correct plugin-specific Structured Output Protocol JSON block, and pass-3 roster check confirmed every agent named in §1 of each CLAUDE.md actually has a corresponding file.

## 6. PRs opened

| PR | Plugin | URL | Head SHA | Status |
|---|---|---|---|---|
| #14 | `finance` | <https://github.com/mcorbett51090/RavenClaude/pull/14> | `b06a4ad` | Open |
| #15 | `regulatory-compliance` | <https://github.com/mcorbett51090/RavenClaude/pull/15> | `946549b` | Open |
| #16 | `web-design` | <https://github.com/mcorbett51090/RavenClaude/pull/16> | `559aa72` | Open |

Each PR's body summarizes its plugin, calls out the polish commit, and includes a test plan. PRs #14 also ships `docs/plugin-roadmap-analysis.md` and this report.

## 7. Honest caveats

- **`marketplace.json` will conflict at merge time.** Each PR bumps `metadata.version` to `0.4.0` and adds its plugin to `plugins[]`. When you merge two, you'll get a conflict on both the version field and the plugin list. Suggested resolution: bump `metadata.version` to `0.6.0` (3 new plugins × MINOR each from `0.3.0`) on the final merged state; concatenate the plugin entries. Same applies to the `docs/architecture.md` Status table (each PR adds a row).
- **`docs/plugin-roadmap-analysis.md` lives on PR #14 only.** PR #15 and #16 reference it but don't include the file. If you merge in a different order, the cross-references in #15 and #16 will be broken for the gap between merges. Easiest fix: merge #14 first, or cherry-pick the analysis-doc commit ahead of the plugins.
- **Sibling-plugin references resolve only after all three merge.** Each plugin's CLAUDE.md mentions the other two as "sibling plugins (when installed alongside)" — phrased to read fine even if a sibling isn't installed, but the markdown link to `../finance/CLAUDE.md` etc. will 404 on a single-plugin branch in isolation. Acceptable per the brief; will fully resolve on main once all three land.
- **CI version-pin cross-check will run.** The `validate-marketplace.yml` workflow checks that each plugin.json's version matches its `marketplace.json` entry. Each branch is self-consistent. Pre-merge, double-check after conflict resolution that all three pins still match.
- **Prettier markdown was deliberately skipped.** Per `.prettierignore`, `*.md` is excluded from prettier — the repo's house position is that markdown style is human-reviewed. My plugins follow that convention. Prettier *will* run on the JSON files I changed; I matched the existing 2-space + `trailingComma: none` JSON style.
- **The Bermuda-insurance specialist's class-tier coverage is broad but reflects my training data.** A practitioner-side review of specific class designations (Class 3 / 3A / 3B / 3M / IIGB definitions and recent rule changes) is worth doing before relying on the plugin in production. The agent applies the Grounding Protocol and would route uncertain questions to counsel anyway, but a sanity pass against current BMA publications is wise.
- **`finance` and `regulatory-compliance` have no behavioral fixtures in `scripts/audit-gates.sh`.** The existing pattern (per `docs/best-practices/ci-gate-audit.md`) is to add a known-bad + known-good fixture per CI gate. My new hooks are advisory-by-default and not run in CI, so this is less critical, but worth adding if you flip either hook to `exit 1`. I tested both manually against bad + good fixtures during the build (`/tmp/{wd,rc,fin}test/...`); the manual results are in commit messages.
- **No live install test.** I didn't run `/plugin marketplace add ./` from a separate Claude Code project (the test plan item left unchecked in each PR). The plugins are structurally identical to `ravenclaude-core` and `power-platform`, so the install path should work, but the only way to be sure is to do it. Suggested as the first review step on each PR.
- **The autonomous run made all judgment calls itself.** Particularly the roster choices (skipping `edtech` + `salesforce`, adding `regulatory-compliance`), the team-roster sizes (6-7 specialists per plugin), and the plugin-specific SOP fields. Worth reviewing the analysis doc + the §3 house opinions in each CLAUDE.md before approving — these are the most opinion-heavy artifacts and the easiest place for a different judgment to land.

## 8. What I'd build next

In priority order, after Matt reviews and merges these three:

1. **CI behavioral tests for the new hooks.** Extend `scripts/audit-gates.sh` and `validate-marketplace.yml` with known-bad + known-good fixtures for the 3 new hooks. Matches the gate-audit-by-fixture rule the repo just codified in `docs/best-practices/ci-gate-audit.md`.
2. **A `cross-plugin-dispatch` doc.** PR #9 (`arch/cross-plugin-dispatch`) is sitting open; with finance ↔ regulatory-compliance ↔ web-design now sharing structured handoffs, the cross-plugin dispatch story is concrete enough to document. Useful for Team Lead in consumer projects that install multiple plugins.
3. **`edtech` plugin** — if a real EdTech engagement comes in, the plugin is well-scoped (partner-success-manager pattern + rostering + FERPA). The team already has the analog (partner-success-manager in `ravenclaude-core`), so this would be additive, not duplicative.
4. **`agentic-ai` plugin** — the marketplace's own existence is the proof-of-craft. A plugin packaging Claude API patterns (prompt caching, tool use, structured outputs, evals) would write itself given the existing `prompt-engineer` agent and the live experience of building these plugins.
5. **Lessons-learned entries from this build.** Two are worth promoting via the staging-contributions flow:
   - "Sibling-plugin cross-references should read as conditional, not hard-link" — a generalizable rule for multi-plugin marketplaces. Topic: `architecture`.
   - "Hook gate-audit fixtures verify on first commit, not on review" — adding bad + good fixtures during the build phase catches polish-pass discoveries earlier. Topic: `testing`.

I'd start with #1, since the existing PR #14 backbone is the new domain plugins, and #1 closes the quality loop the repo already opened.

---

## See also

- [`./plugin-roadmap-analysis.md`](./plugin-roadmap-analysis.md) — the prioritization analysis behind the choice of three.
- [`./architecture.md`](./architecture.md) — Status table updated (per plugin's PR) with the new entry.
- [`./best-practices/plugin-versioning.md`](./best-practices/plugin-versioning.md) — the discipline applied (or noted as a merge-time concern in §7 caveats).
- [`./best-practices/hook-authoring.md`](./best-practices/hook-authoring.md) — the pattern the three new hooks follow.
